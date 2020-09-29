import shapely.wkt

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

    def test_get_downstream_analysis_for_bus13(self):
        assets_bus13 = populate_bus13()
        assets_bus13_geojson = populate_bus13_geojson()
        asset_network = AssetNetwork(
            assets_bus13, assets_bus13_geojson)
        reference_asset_id = 'EFtYFLdR'
        meter_ids, line_geojson = asset_network.get_downstream_analysis(
            reference_asset_id)

        assert len(meter_ids) == 3
        assert len(line_geojson['features']) == 3

    def test_get_downstream_analysis_for_bus13_t(self):
        assets_bus13 = populate_bus13()
        assets_bus13_geojson = populate_bus13_geojson()
        asset_network = AssetNetwork(
            assets_bus13, assets_bus13_geojson)
        reference_asset_id = '3iIAGVcv'
        meter_ids, line_geojson = asset_network.get_downstream_analysis(
            reference_asset_id)

        assert len(meter_ids) == 12
        assert len(line_geojson['features']) == 23


def flat_assets(nested_assets):
    return [item for sublist in nested_assets for item in sublist]


def populate_bus13_geojson():
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets']
    features = []

    for asset in assets:
        shape = shapely.wkt.loads(asset['wkt'])
        features.append({
            "type": "Feature",
            "properties": {
                **asset,
                'name': asset['id'],
                'typeCode': asset['typeCode'],
            },
            "geometry": {
               'type': shape.geom_type,
               'coordinates': shape.coords
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


def populate_bus13():
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets']
    connections = bus13_example['connections']
    populated_assets = []

    for asset in assets:
        populated_assets.append({
            **asset,
            'name': asset['id'],
            'typeCode': asset['typeCode'],
            'connections': get_connections_as_indexed_dict(connections, asset['id'])
        })

    return populated_assets


def get_connections_as_indexed_dict(connections, asset_id):
    connections = list(filter(lambda conn: conn['asset_id'] == asset_id, connections))
    num_connections = len(connections)
    connections_by_index = {}
    for index, connection in zip(range(num_connections), connections):
        connections_by_index[str(index)] = {
            'busId': connection['bus_id'],
            'attributes': connection['attributes'],
            'asset_vertex_index': connection['asset_vertex_index']
        }

    return connections_by_index


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
