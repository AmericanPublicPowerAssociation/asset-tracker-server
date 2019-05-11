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
    return {}


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
