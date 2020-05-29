import numpy as np
from collections import defaultdict
from functools import lru_cache, reduce
from networkx import Graph, shortest_path
from shapely.geometry import LineString

from ..macros.geometry import get_line_length_in_meters
from ..macros.iterable import PairSet, get_adjacent_pairs
from ..models import AssetTypeCode


class AssetNetwork(object):

    def __init__(self, asset_dictionaries, assets_geojson):
        g = Graph()
        for asset_dictionary in asset_dictionaries:
            connections = asset_dictionary['connections']
            sorted_connections = sorted(connections.items())
            adjacent_pairs = get_adjacent_pairs(sorted_connections)
            for connection_pack1, connection_pack2 in adjacent_pairs:
                bus1_id = connection_pack1[1]['busId']
                bus2_id = connection_pack2[1]['busId']
                g.add_edge(bus1_id, bus2_id)

        asset_ids_by_type_value = defaultdict(set)
        for asset_dictionary in asset_dictionaries:
            asset_id = asset_dictionary['id']
            type_value = asset_dictionary['typeCode']
            asset_ids_by_type_value[type_value].add(asset_id)

        bus_ids_by_asset_id = defaultdict(set)
        for asset_dictionary in asset_dictionaries:
            asset_id = asset_dictionary['id']
            connections = asset_dictionary['connections']
            bus_ids_by_asset_id[asset_id].update(
                _['busId'] for _ in connections.values())

        line_dictionaries = [
            _ for _ in asset_dictionaries
            if _['typeCode'] == AssetTypeCode.LINE.value]

        asset_features = assets_geojson['features']
        try:
            line_asset_ids = asset_ids_by_type_value[AssetTypeCode.LINE.value]
        except KeyError:
            line_asset_ids = []
        line_features = [
            _ for _ in asset_features
            if _['properties']['id'] in line_asset_ids]
        line_feature_by_asset_id = {
            _['properties']['id']: _ for _ in line_features}

        line_ids_by_bus_id = defaultdict(set)
        vertex_index_by_line_id_bus_id = {}
        for line_dictionary in line_dictionaries:
            line_id = line_dictionary['id']
            line_connections = line_dictionary['connections']
            for vertex_index, connection in line_connections.items():
                bus_id = connection['busId']
                line_ids_by_bus_id[bus_id].add(line_id)
                vertex_index_by_line_id_bus_id[(line_id, bus_id)] = int(
                    vertex_index)

        self.asset_ids_by_type_value = asset_ids_by_type_value
        self.bus_graph = g
        self.bus_ids_by_asset_id = bus_ids_by_asset_id
        self.line_feature_by_asset_id = line_feature_by_asset_id
        self.line_ids_by_bus_id = line_ids_by_bus_id
        self.vertex_index_by_line_id_bus_id = vertex_index_by_line_id_bus_id

    def prepare_downstream_analysis(self, reference_asset_id):
        downstream_packs = self.get_downstream_packs(
            reference_asset_id, AssetTypeCode.METER.value)
        meter_ids = [_[0] for _ in downstream_packs]
        target_edges = reduce(
            lambda all_edges, new_edges: PairSet(all_edges).union(new_edges),
            [_[1] for _ in downstream_packs]) if downstream_packs else set()
        line_features = self.get_geojson_features_from_edges(target_edges)
        line_geojson = {'type': 'FeatureCollection', 'features': line_features}
        return meter_ids, line_geojson

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
        generator_edges = PairSet()
        for generator_bus_id in generator_bus_ids:
            paths = []
            for reference_bus_id in reference_bus_ids:
                path_bus_ids = shortest_path(
                    self.bus_graph, generator_bus_id, reference_bus_id)
                paths.append(path_bus_ids)
            chosen_path = choose_shortest_path(paths)
            print('GENERATOR', chosen_path)
            generator_edges.update(get_adjacent_pairs(chosen_path))

        # Get shortest path between the reference asset and each target asset
        downstream_packs = set()
        for target_asset_id in target_asset_ids:
            target_edges = PairSet()
            try:
                target_bus_ids = self.bus_ids_by_asset_id[target_asset_id]
            except KeyError:
                continue
            for target_bus_id in target_bus_ids:
                paths = []
                for reference_bus_id in reference_bus_ids:
                    path_bus_ids = shortest_path(
                        self.bus_graph, reference_bus_id, target_bus_id)
                    paths.append(path_bus_ids)
                chosen_path = choose_shortest_path(paths)
                print('TARGET', chosen_path)
                target_edges.update(get_adjacent_pairs(chosen_path))
            # If there is no edge overlap, then we have a downstream asset
            if not generator_edges.intersection(target_edges):
                downstream_packs.add((target_asset_id, tuple(target_edges)))
        return downstream_packs

    @lru_cache()
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

    def get_geojson_features_from_edges(self, bus_edges):
        geojson_features = []
        for bus1_id, bus2_id in bus_edges:
            try:
                bus1_line_ids = self.line_ids_by_bus_id[bus1_id]
                bus2_line_ids = self.line_ids_by_bus_id[bus2_id]
            except KeyError:
                continue
            line_ids = bus1_line_ids.intersection(bus2_line_ids)
            if not line_ids:
                continue
            line_packs = []
            for line_id in line_ids:
                vertex1_index = self.vertex_index_by_line_id_bus_id[(
                    line_id, bus1_id)]
                vertex2_index = self.vertex_index_by_line_id_bus_id[(
                    line_id, bus2_id)]
                vertex1_index, vertex2_index = sorted((
                    vertex1_index, vertex2_index))
                line_feature = self.line_feature_by_asset_id[line_id]
                old_line_xys = line_feature['geometry']['coordinates']
                new_line_xys = old_line_xys[vertex1_index:vertex2_index + 1]
                line_geometry = LineString(new_line_xys)
                line_length_in_meters = get_line_length_in_meters(
                    line_geometry)
                line_packs.append((line_length_in_meters, line_geometry))
            best_line_geometry = sorted(line_packs)[0][1]
            geojson_features.append({
                'type': 'Feature',
                'geometry': best_line_geometry.__geo_interface__,
            })
        return geojson_features


def choose_shortest_path(paths):
    path_lengths = [len(path) for path in paths]
    selected_index = np.argmin(path_lengths)
    return paths[selected_index]
