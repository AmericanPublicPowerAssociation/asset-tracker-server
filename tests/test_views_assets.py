import json
from asset_tracker.models import Asset
from asset_tracker.views.assets import change_assets_json
from os.path import join

from conftest import DATASETS_FOLDER


ASSET_JSON_PATH = join(DATASETS_FOLDER, 'assets1.json')
ASSET_GEOJSON_PATH = join(DATASETS_FOLDER, 'assets1.geojson')


ASSET_DICTIONARIES = json.load(open(ASSET_JSON_PATH, 'rt'))
ASSET_FEATURE_COLLECTION = json.load(open(ASSET_GEOJSON_PATH, 'rt'))


class TestChangeAssetsJson(object):

    def test_accept_parameters(self, db):
        '''
        website_request.json_body = {
            'assets': ASSET_DICTIONARIES,
            'assetsGeoJson': ASSET_FEATURE_COLLECTION,
        }
        # assert db.query(Asset).count() == 0
        # website_response_d = change_assets_json(website_request)
        # assert db.query(Asset).count() == 4
        '''
