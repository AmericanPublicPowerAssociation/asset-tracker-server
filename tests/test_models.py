from asset_tracker.models import Asset
from asset_tracker.views.assets import add_asset_json


class TestAddAssetJson(object):

    def test_accept_parameters(self, website_request, db):
        website_request.json_body = {
            'utilityId': 'a', 'typeId': 'p', 'name': 'POLE'}
        assert db.query(Asset).count() == 0
        add_asset_json(website_request)
        assert db.query(Asset).count() == 1
