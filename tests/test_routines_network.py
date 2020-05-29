from asset_tracker.models import AssetTypeCode
from asset_tracker.routines.network import AssetNetwork, get_geojson_from_edges

from conftest import EXAMPLE_BY_NAME, get_asset_dictionaries


EXAMPLE = EXAMPLE_BY_NAME['basic']
EXAMPLE_ASSET_BY_ID = EXAMPLE['assetById']
EXAMPLE_ASSETS_GEOJSON = EXAMPLE['assetsGeoJson']
EXAMPLE_ASSET_DICTIONARIES = get_asset_dictionaries(EXAMPLE_ASSET_BY_ID)


class TestAssetNetwork(object):

    def test_get_downstream_packs(self):
        asset_network = AssetNetwork(EXAMPLE_ASSET_DICTIONARIES)
        # Get meters downstream of transformer
        reference_asset_id = 'DaBGRPemyBnRWeCy1590713640634'
        downstream_packs = asset_network.get_downstream_packs(
            reference_asset_id, AssetTypeCode.METER.value)
        downstream_meter_ids = [_[0] for _ in downstream_packs]
        assert len(downstream_meter_ids) == 3


def test_get_geojson_from_edges():
    bus_edges = [(
        'yiltSxjZCZegScHGOYCVGKXbvWmYB3s51590713649457',
        'mxscsJBUYseJZdp675GrWDFU8wEd9nl61590713647194',
    )]
    line_dictionaries = [
        _ for _ in EXAMPLE_ASSET_DICTIONARIES
        if _['typeCode'] == 'l']
    line_geojsons = [
        _ for _ in EXAMPLE_ASSETS_GEOJSON['features']
        if _['properties']['typeCode'] == 'l']
    feature_collection = get_geojson_from_edges(
        bus_edges, line_dictionaries, line_geojsons)
    features = feature_collection['features']
    assert len(features) == 1
    assert len(features[0]['geometry']['coordinates']) == 2
