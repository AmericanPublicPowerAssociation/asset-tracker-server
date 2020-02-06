from pytest import raises
from pyramid.exceptions import HTTPBadRequest
from asset_tracker.views.assets import add_asset_json


class TestAddAssetJson(object):
    def test_accept_parameters(self, website_request, db):
        website_request.json_body = {
            'utilityId': 'a',
            'typeId': 'p',
            'name': 'POLE', }
        assert db.query(Asset).count() == 0
        add_asset_json(website_request)
        assert db.query(Asset).count() == 1

    def test_missing_utilityId_param(self, website_request):
        with raises(HTTPBadRequest) as excinfo:
            website_request.json_body = {
                'typeId': 'p',
                'name': 'Pole', }
            add_asset_json(website_request)
        assert "'utilityId': 'is required'" in str(excinfo.value)
    
    def test_missing_typeId_param(self, website_request):
        with raises(HTTPBadRequest) as excinfo:
            website_request.json_body = {
                'utilityId': 'a',
                'name': 'Pole', }
            add_asset_json(website_request)
        assert "'typeId': 'is required'" in str(excinfo.value)

    def test_missing_name_param(self, website_request):
        with raises(HTTPBadRequest) as excinfo:
            website_request.json_body = {
                'utilityId': 'a',
                'typeId': 'p', }
            add_asset_json(website_request)
        assert "'name': 'is required'" in str(excinfo.value)
