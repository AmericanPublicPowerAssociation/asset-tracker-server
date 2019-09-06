from asset_tracker.models import Asset
from asset_tracker.models import AssetTask
from asset_tracker.views.assets import add_asset_json
from asset_tracker.views.tasks import add_task_json


class TestAddAssetJson(object):

    def test_accept_parameters(self, website_request, db):
        website_request.json_body = {
            'utilityId': 'a', 'typeId': 'p', 'name': 'POLE'}
        assert db.query(Asset).count() == 0
        add_asset_json(website_request)
        assert db.query(Asset).count() == 1


class TestAddTaskJson(object):
    def test_accept_parameters(self, website_request, db):
        website_request.json_body = {
            'utilityId': 'a', 'typeId': 'p', 'name': 'POLE'}
        assert db.query(Asset).count() == 0
        r = add_asset_json(website_request)

        website_request.json_body = {
            # 'id': 'x',
            'referenceId': 'b',
            'assetId': r['id'],
            'userId': 'k',
            'name': 'regular maintenance',
            'status': 0,
            'description': 's',
        }
        assert db.query(AssetTask).count() == 0
        add_task_json(website_request)
        assert db.query(AssetTask).count() == 1
