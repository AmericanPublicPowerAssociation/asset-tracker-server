from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..models import Asset


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    db = request.db
    return [{
        'id': asset.id,
        'typeId': asset.type_id,
        'name': asset.name,
    } for asset in db.query(Asset)]


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='GET')
def see_asset_json(request):
    return {}


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='POST')
def add_asset_json(request):
    params = request.json_body
    # !!! get utility id
    try:
        asset_type_id = params['typeId']
    except KeyError:
        raise HTTPBadRequest({'typeId': 'is required'})
    # !!! check valid type id
    try:
        asset_name = params['name']
    except KeyError:
        # !!! consider filling asset name automatically
        raise HTTPBadRequest({'name': 'is required'})
    # !!! check that name is unique within utility
    db = request.db
    asset = Asset.make_unique_record(db)
    asset.type_id = asset_type_id
    asset.name = asset_name
    db.flush()
    return {
        'id': asset.id,
        'typeId': asset.type_id,
        'name': asset.name,
    }


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='PATCH')
def change_asset_json(request):
    return {}


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='DELETE')
def drop_asset_json(request):
    return {}
