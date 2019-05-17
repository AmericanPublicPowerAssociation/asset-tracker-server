from pyramid.httpexceptions import (
    HTTPBadRequest, HTTPInsufficientStorage)
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from ..exceptions import DatabaseRecordError
from ..macros.text import compact_whitespace
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
    try:
        utility_id = params['utilityId']
    except KeyError:
        raise HTTPBadRequest({'utilityId': 'is required'})
    # !!! check valid utility id
    try:
        asset_type_id = params['typeId']
    except KeyError:
        raise HTTPBadRequest({'typeId': 'is required'})
    # !!! check valid type id
    try:
        asset_name = compact_whitespace(params['name']).strip()
    except KeyError:
        # !!! consider filling asset name automatically
        raise HTTPBadRequest({'name': 'is required'})
    if not asset_name:
        raise HTTPBadRequest({'name': 'cannot be empty'})
    db = request.db
    if db.query(Asset.name.ilike(asset_name)).count():
        raise HTTPBadRequest({'name': 'must be unique within utility'})
    try:
        asset = Asset.make_unique_record(db)
    except DatabaseRecordError:
        raise HTTPInsufficientStorage({'asset': 'could not make unique id'})
    asset.utility_id = utility_id
    asset.type_id = asset_type_id
    asset.name = asset_name
    try:
        db.flush()
    except IntegrityError:
        raise HTTPBadRequest({'name': 'must be unique within utility'})
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
