from collections import defaultdict
from functools import lru_cache
from networkx import Graph, shortest_path
from shapely.geometry import LineString

from ..macros.geometry import get_line_length_in_meters
from ..macros.iterable import get_adjacent_pairs
from ..models import AssetTypeCode


class AssetNetwork(object):

    def __init__(self, asset_dictionaries):
        g = Graph()
        asset_ids_by_type_value = defaultdict(set)
        bus_ids_by_asset_id = defaultdict(set)
        for asset_dictionary in asset_dictionaries:
            asset_id = asset_dictionary['id']
            type_value = asset_dictionary['typeCode'].value
            asset_ids_by_type_value[type_value].add(asset_id)
            connections = asset_dictionary['connections']
            sorted_connections = sorted(connections.items())
            adjacent_pairs = get_adjacent_pairs(sorted_connections)
            for connection_pack1, connection_pack2 in adjacent_pairs:
                # vertex1_index = connection_pack1[0]
                bus1_id = connection_pack1[1]['busId']
                # vertex2_index = connection_pack2[0]
                bus2_id = connection_pack2[1]['busId']
                g.add_edge(bus1_id, bus2_id)
                bus_ids_by_asset_id[asset_id].update([bus1_id, bus2_id])
        self.asset_ids_by_type_value = asset_ids_by_type_value
        self.bus_graph = g
        self.bus_ids_by_asset_id = bus_ids_by_asset_id

    def get_downstream_packs(self, reference_asset_id, asset_type_value):
        try:
            reference_bus_ids = self.bus_ids_by_asset_id[reference_asset_id]
        except KeyError:
            return set()
        try:
            target_asset_ids = self.asset_ids_by_type_value[asset_type_value]
        except KeyError:
            return set()

        # Get shortest paths between each generator and the reference asset
        generator_bus_ids = self.get_bus_ids_by_type_value(
            AssetTypeCode.GENERATOR.value)
        generator_edges = set()
        for generator_bus_id in generator_bus_ids:
            for reference_bus_id in reference_bus_ids:
                path_bus_ids = shortest_path(
                    self.bus_graph, generator_bus_id, reference_bus_id)
                generator_edges.update(get_adjacent_pairs(path_bus_ids))

        # Get shortest path between the reference asset and each target asset
        downstream_packs = set()
        for target_asset_id in target_asset_ids:
            target_edges = set()
            try:
                target_bus_ids = self.bus_ids_by_asset_id[target_asset_id]
            except KeyError:
                continue
            for target_bus_id in target_bus_ids:
                for reference_bus_id in reference_bus_ids:
                    path_bus_ids = shortest_path(
                        self.bus_graph, reference_bus_id, target_bus_id)
                    target_edges.update(get_adjacent_pairs(path_bus_ids))
            # If there is no edge overlap, then we have a downstream asset
            if not generator_edges.intersection(target_edges):
                downstream_packs.add((target_asset_id, target_edges))
        return downstream_packs

    @lru_cache
    def get_bus_ids_by_type_value(self, type_value):
        bus_ids = set()
        try:
            asset_ids = self.asset_ids_by_type_value[type_value]
        except KeyError:
            return bus_ids
        for asset_id in asset_ids:
            bus_ids = self.bus_ids_by_asset_id[asset_id]
            bus_ids.update(bus_ids)
        return bus_ids


def get_geojson_from_edges(bus_edges, line_dictionaries, line_geojsons):
    # Prepare lookup tables
    line_dictionary_by_asset_id = {}
    line_geojson_by_asset_id = {
        _['properties']['id']: _ for _ in line_geojsons}
    line_ids_by_bus_id = defaultdict(set)
    vertex_index_by_line_id_bus_id = {}
    for line_dictionary in line_dictionaries:
        line_id = line_dictionary['id']
        for vertex_index, connection in line_dictionary['connections'].items():
            bus_id = connection['busId']
            line_ids_by_bus_id[bus_id].add(line_id)
            vertex_index_by_line_id_bus_id[(line_id, bus_id)] = vertex_index
        line_dictionary_by_asset_id[line_id] = line_dictionary
    # Gather geojson features
    geojson_features = []
    for bus1_id, bus2_id in bus_edges:
        try:
            bus1_line_ids = line_ids_by_bus_id[bus1_id]
            bus2_line_ids = line_ids_by_bus_id[bus2_id]
        except KeyError:
            continue
        line_ids = bus1_line_ids.intersection(bus2_line_ids)
        if not line_ids:
            continue
        line_packs = []
        for line_id in line_ids:
            vertex1_index = vertex_index_by_line_id_bus_id[(line_id, bus1_id)]
            vertex2_index = vertex_index_by_line_id_bus_id[(line_id, bus2_id)]
            vertex1_index, vertex2_index = sorted((
                vertex1_index, vertex2_index))
            line_geojson = line_geojson_by_asset_id[line_id]
            old_line_xys = line_geojson['geometry']['coordinates']
            new_line_xys = old_line_xys[vertex1_index:vertex2_index + 1]
            line_geometry = LineString(new_line_xys)
            line_length_in_meters = get_line_length_in_meters(line_geometry)
            line_packs.append((line_length_in_meters, line_geometry))
        best_line_geometry = sorted(line_packs)[0][1]
        geojson_features.append({
            'type': 'Feature',
            'geometry': best_line_geometry.__geo_interface__,
        })
    return {'type': 'FeatureCollection', 'features': geojson_features}
