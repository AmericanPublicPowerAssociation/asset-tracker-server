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
        return self.request.db.query(Asset).filter_by(deleted=False)
    
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
            if updated_asset.get('name', None):
                db_asset.name = updated_asset['name']
            if updated_asset.get('typeCode', None):
                db_asset.type_code = updated_asset['typeCode']
            if updated_asset.get('delete', None):
                db_asset.deleted = updated_asset['delete']
            if updated_asset.get('attributes', None):
                db_asset.attributes = updated_asset['attributes']
            self.request.db.add(db_asset)
        assets = self.query.options(
            selectinload(Asset.connections)).all()
        return [_.get_json_d() for _ in assets]
    
    @view_config(request_method='DELETE')
    def delete(self):
        params = self.request.json_body
        deleted_assets = self.get_required_param(
            'deletedAssets', params, list)
        db_assets = self.request.db.query(Asset).filter(
            Asset.id.in_(deleted_assets)).all()
        for db_asset in db_assets:
            db_asset.deleted = True
            self.request.db.add(db_asset) 
        assets = self.query.options(
            selectinload(Asset.connections)).all()
        return [_.get_json_d() for _ in assets]

    @view_config(route_name='asset_delete')
    def delete_asset(self):
        asset_id = self.request.matchdict['id']
        db_asset = self.query.filter(Asset.id==asset_id).first()
        if db_asset is None:
            raise HTTPBadRequest('asset_id invalid')
        if db_asset.deleted:
            raise HTTPBadRequest('invalid operation')
        db_asset.deleted = True
        self.request.db.add(db_asset)
        self.request.db.flush()
        return {'deleted': asset_id}


    @view_config(request_method='POST')
    def post(self):
        params = self.request.json_body
        new_assets = self.get_required_param(
            'newAssets', params, list)
        for asset in new_assets:
            import time
            asset_id = str(time.time())
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
            asset_db.attributes = asset.get('attributes', None)
            asset_db.deleted = asset.get('deleted', False)
            # TODO add connections to asset
            self.request.db.add(asset_db)
        self.request.db.flush()
        assets = self.query.options(
            selectinload(Asset.connections)
        ).all()
        return [_.get_json_d() for _ in assets]
