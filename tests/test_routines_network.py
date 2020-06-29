from asset_tracker.routines.network import (
    AssetNetwork,
    choose_shortest_path,
    get_bus_graph)

from conftest import EXAMPLE_BY_NAME, get_asset_dictionaries


EXAMPLE = EXAMPLE_BY_NAME['basic']
EXAMPLE_ASSET_BY_ID = EXAMPLE['assetById']
EXAMPLE_ASSETS_GEOJSON = EXAMPLE['assetsGeoJson']
EXAMPLE_ASSET_DICTIONARIES = get_asset_dictionaries(EXAMPLE_ASSET_BY_ID)


class TestAssetNetwork(object):

    def test_get_downstream_analysis(self):
        asset_network = AssetNetwork(
            EXAMPLE_ASSET_DICTIONARIES, EXAMPLE_ASSETS_GEOJSON)
        reference_asset_id = 'transformer'
        meter_ids, line_geojson = asset_network.get_downstream_analysis(
            reference_asset_id)
        assert len(meter_ids) == 3
        assert len(line_geojson['features']) == 3


def test_get_bus_graph():
    bus_graph = get_bus_graph([{
        'connections': {
            2: {'busId': 'a'},
            0: {'busId': 'b'},
            3: {'busId': 'c'},
        },
    }, {
        'connections': {
            3: {'busId': 'c'},
            1: {'busId': 'a'},
        },
    }])
    bus_graph_edges = bus_graph.edges()
    assert 'a' in bus_graph
    assert 'b' in bus_graph
    assert 'c' in bus_graph
    assert ('a', 'b') in bus_graph_edges
    assert ('a', 'c') in bus_graph_edges
    assert ('b', 'c') not in bus_graph_edges


def test_choose_shortest_path():
    assert choose_shortest_path([[1, 2], [9], [2, 1, 2]]) == [9]
