from collections import defaultdict
from networkx import Graph

from ..macros.iterable import get_adjacent_pairs


class AssetNetwork(object):

    def __init__(self, asset_dictionaries):
        g = Graph()
        bus_ids_by_asset_id = defaultdict(set)
        for asset_dictionary in asset_dictionaries:
            asset_id = asset_dictionary['id']
            connections = asset_dictionary['connections']
            sorted_connections = sorted(connections.items())
            adjacent_pairs = get_adjacent_pairs(sorted_connections)
            for (connection_pack1, connection_pack2) in adjacent_pairs:
                # vertex1_index = connection_pack1[0]
                bus1_id = connection_pack1[1]['busId']
                # vertex2_index = connection_pack2[0]
                bus2_id = connection_pack2[1]['busId']
                g.add_edge(bus1_id, bus2_id)
                bus_ids_by_asset_id[asset_id].update(bus1_id, bus2_id)
        self.bus_graph = g
        self.bus_ids_by_asset_id = bus_ids_by_asset_id

    def get_downstream_asset_ids(self, reference_asset_id, asset_type_code):
        pass
