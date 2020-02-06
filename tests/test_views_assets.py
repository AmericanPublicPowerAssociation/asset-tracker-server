from asset_tracker.views.assets import change_assets_json

from conftest import EXAMPLE_BY_NAME


class TestSeeAssetsJson(object):

    def test_accept_parameters(self, website_request, db):
        pass


class TestChangeAssetsJson(object):

    def test_accept_parameters(self, website_request, db):
        example = EXAMPLE_BY_NAME['basic']
        old_asset_dictionaries = example['assets']
        old_asset_feature_collection = example['assetsGeoJson']
        website_request.json_body = {
            'assets': old_asset_dictionaries,
            'assetsGeoJson': old_asset_feature_collection,
        }
        website_response_d = change_assets_json(website_request)

        new_asset_dictionaries = website_response_d['assets']
        new_asset_dictionary_by_name = {
            _['name']: _ for _ in new_asset_dictionaries}
        new_asset_feature_collection = website_response_d['assetsGeoJson']
        assert len(old_asset_dictionaries) == len(new_asset_dictionaries)

        for old_asset_dictionary in old_asset_dictionaries:
            new_asset_dictionary = new_asset_dictionary_by_name[
                old_asset_dictionary['name']]
            assert len(old_asset_dictionary['attributes']) == len(
                new_asset_dictionary['attributes'])
            assert len(old_asset_dictionary['connections']) == len(
                new_asset_dictionary['connections'])

        old_asset_features = old_asset_feature_collection['features']
        new_asset_features = new_asset_feature_collection['features']
        assert len(old_asset_features) == len(new_asset_features)
