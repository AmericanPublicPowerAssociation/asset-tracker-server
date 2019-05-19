from pyramid.httpexceptions import (
    HTTPBadRequest, HTTPInsufficientStorage, HTTPNotFound)
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from ..exceptions import DatabaseRecordError
from ..macros.text import normalize_text
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


'''
@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='GET')
def see_asset_json(request):
    return {}
'''


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
    # !!! check whether user can add assets to utility id
    try:
        type_id = params['typeId']
    except KeyError:
        raise HTTPBadRequest({'typeId': 'is required'})
    # !!! check valid type id
    db = request.db
    try:
        name = params['name']
    except KeyError:
        # !!! consider filling asset name automatically
        raise HTTPBadRequest({'name': 'is required'})
    else:
        name = validate_name(db, name, utility_id)
    try:
        asset = Asset.make_unique_record(db)
    except DatabaseRecordError:
        raise HTTPInsufficientStorage({'asset': 'could not make unique id'})
    asset.utility_id = utility_id
    asset.type_id = type_id
    asset.name = name
    try:
        db.flush()
    except IntegrityError:
        raise HTTPBadRequest({'name': 'must be unique within utility'})
    return asset.serialize()


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='PATCH')
def change_asset_json(request):
    params = request.json_body
    try:
        id = params['id']
    except KeyError:
        raise HTTPBadRequest({'id': 'is required'})
    db = request.db
    asset = db.query(Asset).get(id)
    if not asset:
        raise HTTPNotFound({'id': 'does not exist'})
    utility_id = asset.utility_id
    # !!! check whether user can update this asset
    try:
        name = params['name']
    except KeyError:
        pass
    else:
        asset.name = validate_name(db, name, utility_id)
    return asset.serialize()


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='DELETE')
def drop_asset_json(request):
    return {}


def validate_name(db, name, utility_id):
    name = normalize_text(name)
    if not name:
        raise HTTPBadRequest({'name': 'cannot be empty'})
    if db.query(Asset).filter(
        Asset.utility_id == utility_id,
        Asset.name.ilike(name),
    ).count():
        raise HTTPBadRequest({'name': 'must be unique within utility'})
    return name
