from pyramid.httpexceptions import (
    HTTPBadRequest, HTTPInsufficientStorage, HTTPNotFound)
from pyramid.view import view_config

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
    return asset.serialize()


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='PATCH')
def change_asset_json(request):
    matchdict = request.matchdict
    params = request.json_body
    db = request.db

    id = matchdict['id']
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
        asset.name = validate_name(db, name, utility_id, id)
    return asset.serialize()


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='DELETE')
def drop_asset_json(request):
    return {}


@view_config(
    route_name='asset_relation.json',
    renderer='json',
    request_method='PATCH')
@view_config(
    route_name='asset_relation.json',
    renderer='json',
    request_method='DELETE')
def change_asset_relation_json(request):
    matchdict = request.matchdict
    db = request.db
    method = request.method

    id = matchdict['id']
    asset = db.query(Asset).get(id)
    if not asset:
        raise HTTPNotFound({'id': 'does not exist'})

    target_id = matchdict['other_id']
    target_asset = db.query(Asset).get(target_id)
    if not target_asset:
        raise HTTPNotFound({'other_id': 'does not exist'})

    # !!! Check edit permissions for both assets

    type = matchdict['type']
    if 'childIds' == type:
        if method == 'PATCH':
            asset.add_child(target_asset)
        elif method == 'DELETE':
            asset.remove_child(target_asset)
    elif 'parentIds' == type:
        if method == 'PATCH':
            target_asset.add_child(asset)
        elif method == 'DELETE':
            target_asset.remove_child(asset)
    elif 'connectedIds' == type:
        if method == 'PATCH':
            asset.add_connection(target_asset)
        elif method == 'DELETE':
            asset.remove_connection(target_asset)
    else:
        raise HTTPBadRequest({'type': 'is not recognized'})
    return {}


def validate_name(db, name, utility_id, id=None):
    name = normalize_text(name)
    if not name:
        raise HTTPBadRequest({'name': 'cannot be empty'})
    duplicate_query = db.query(Asset).filter(
        Asset.utility_id == utility_id, Asset.name.ilike(name))
    if id:
        duplicate_query = duplicate_query.filter(Asset.id != id)
    if duplicate_query.count():
        raise HTTPBadRequest({'name': 'must be unique within utility'})
    return name
