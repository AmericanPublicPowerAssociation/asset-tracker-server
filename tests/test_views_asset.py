from asset_tracker.views.asset import change_assets_json

from conftest import EXAMPLE_BY_NAME


class TestChangeAssetsJson(object):

    def test_accept_parameters(self, application_request):
        example = EXAMPLE_BY_NAME['basic']
        old_asset_dictionary_by_id = example['assetById']
        old_asset_feature_collection = example['assetsGeoJson']
        old_asset_features = old_asset_feature_collection['features']
        application_request.json_body = {
            'assetById': old_asset_dictionary_by_id,
            'assetsGeoJson': old_asset_feature_collection,
        }
        application_response_d = change_assets_json(application_request)
        new_asset_dictionary_by_id = application_response_d['assetById']
        new_asset_feature_collection = application_response_d['assetsGeoJson']
        new_asset_features = new_asset_feature_collection['features']

        assert len(old_asset_dictionary_by_id) == len(
            new_asset_dictionary_by_id)
        new_asset_dictionary_by_name = {
            _['name']: _ for _ in new_asset_dictionary_by_id.values()}
        for old_asset_dictionary in old_asset_dictionary_by_id.values():
            new_asset_dictionary = new_asset_dictionary_by_name[
                old_asset_dictionary['name']]
            assert len(old_asset_dictionary.get('attributes', [])) == len(
                new_asset_dictionary.get('attributes', []))
            assert len(old_asset_dictionary.get('connections', [])) == len(
                new_asset_dictionary.get('connections', []))
        assert len(old_asset_features) == len(new_asset_features)
