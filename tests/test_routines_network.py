from asset_tracker.routines.network import AssetNetwork

from conftest import EXAMPLE_BY_NAME, get_asset_dictionaries


EXAMPLE = EXAMPLE_BY_NAME['basic']
EXAMPLE_ASSET_BY_ID = EXAMPLE['assetById']
EXAMPLE_ASSETS_GEOJSON = EXAMPLE['assetsGeoJson']
EXAMPLE_ASSET_DICTIONARIES = get_asset_dictionaries(EXAMPLE_ASSET_BY_ID)


class TestAssetNetwork(object):

    def test_get_downstream_meter_ids_and_line_geojson(self):
        asset_network = AssetNetwork(
            EXAMPLE_ASSET_DICTIONARIES, EXAMPLE_ASSETS_GEOJSON)
        reference_asset_id = 'transformer'
        meter_ids, line_geojson = asset_network.prepare_downstream_analysis(
            reference_asset_id)
        assert len(meter_ids) == 3
        assert len(line_geojson['features']) == 3
