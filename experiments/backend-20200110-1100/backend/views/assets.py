from pyramid.view import (
    view_config,
    view_defaults
    )
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm import selectinload
from backend.models import (Asset)


@view_defaults(
    route_name='assets.json',
    renderer='json')
class AssetsViews:
    def __init__(self, request):
        self.request = request

    @property
    def query(self):
        return self.request.db.query(Asset)
    
    def get_required_param(self, key, obj, obj_type):
        try:
            param = obj[key]
        except KeyError:
            raise HTTPBadRequest({key: 'is required'})
        if not isinstance(obj[key], obj_type):
            raise HTTPBadRequest({key: ('must be %s' % obj_type.__name__)})
        return param

    @view_config(request_method='GET')
    def get(self):
        assets = self.query.options(
            selectinload(Asset.connections)).all()
        return [_.get_json_d() for _ in assets]

    @view_config(request_method='PATCH')
    def patch(self):
        params = self.request.json_body
        asset_ids = self.get_required_param('assetIds', params, list)
        updated_assets = self.get_required_param(
            'updatedAssets', params, dict)
        db_assets = self.query.filter(Asset.id.in_(asset_ids)).all()
        for db_asset in db_assets:
            # traverse and update in db
            updated_asset = updated_assets[db_asset.id]
            db_asset.name = updated_asset['name']
            db_asset.type_code = updated_asset['typeCode']
            self.request.db.add(db_asset)
        assets = self.query.options(
            selectinload(Asset.connections)).all()
        return [_.get_json_d() for _ in assets]
    
    @view_config(request_method='DELETE')
    def delete(self):
        assets = self.query.all()  # will flush updated assets 
        # TODO
        return {'assets': assets}

    @view_config(request_method='POST')
    def post(self):
        params = self.request.json_body
        new_assets = self.get_required_param('newAssets', params, list)
        for asset in new_assets:
            try:
                asset_id = asset['id']
            except KeyError:
                raise HTTPBadRequest({'id': 'is required'})
            try:
                name = asset['name']
            except KeyError:
                raise HTTPBadRequest({'name': 'is required'})
            try:
                type_code = asset['typeCode']
            except KeyError:
                raise HTTPBadRequest({'typeCode': 'is required'})
            # TODO handle duplicates
            asset_db = Asset()
            asset_db.id = asset_id
            asset_db.name = name
            asset_db.type_code = type_code
            if asset.get('attributes'):
                asset_db.attributes = asset['attributes']
            # TODO add connections to asset
            self.request.db.add(asset_db)
            self.request.db.flush()
        assets = self.query.options(
            selectinload(Asset.connections)
        ).all()
        return [_.get_json_d() for _ in assets]
