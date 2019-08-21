from pyramid.httpexceptions import (
    HTTPBadRequest, HTTPInsufficientStorage, HTTPNotFound)
from pyramid.view import view_config

from ..constants import ASSET_TYPES
from ..exceptions import DatabaseRecordError
from ..macros.text import normalize_text
from ..models import Asset
from ..routines.geometry import get_bounding_box


@view_config(
    route_name='assets_kit.json',
    renderer='json',
    request_method='GET')
def see_assets_kit_json(request):
    assets = see_assets(request)
    bounding_box = get_bounding_box(assets)
    return {
        'assetTypes': see_asset_types_json(request),
        'assets': [_.serialize() for _ in assets],
        'boundingBox': bounding_box,
    }


@view_config(
    route_name='asset_types.json',
    renderer='json',
    request_method='GET')
def see_asset_types_json(request):
    return ASSET_TYPES


def see_assets(request):
    db = request.db
    return db.query(Asset).all()


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    assets = see_assets(request)
    return [_.serialize() for _ in assets]


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
    params = dict(request.json_body)
    db = request.db

    id = matchdict['id']
    asset = db.query(Asset).get(id)
    if not asset:
        raise HTTPNotFound({'id': 'does not exist'})
    changed_assets = [asset]

    utility_id = asset.utility_id

    # !!! Check whether user can update this asset

    try:
        name = params.pop('name')
    except KeyError:
        pass
    else:
        asset.name = validate_name(db, name, utility_id, id)

    try:
        location = params.pop('location')
    except KeyError:
        pass
    else:
        if not asset.is_locatable:
            raise HTTPBadRequest({
                'location': 'is not accepted for this asset type'})
        asset.location = location
        changed_assets.extend(asset.parents)
        changed_assets.extend(asset.children)

    params.pop('id', None)
    params.pop('typeId', None)
    params.pop('connectedIds', None)
    params.pop('parentIds', None)
    params.pop('childIds', None)

    attributes = dict(asset.attributes or {})
    for k, v in params.items():
        if v is None:
            attributes.pop(k, None)
            continue
        attributes[k] = v
    asset.attributes = attributes

    return [_.serialize() for _ in changed_assets]


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

    other_id = matchdict['otherId']
    other_asset = db.query(Asset).get(other_id)
    if not other_asset:
        raise HTTPNotFound({'otherId': 'does not exist'})

    # !!! Check edit permissions for both assets

    key = matchdict['key']
    if 'childIds' == key:
        if method == 'PATCH':
            asset.add_child(other_asset)
        elif method == 'DELETE':
            asset.remove_child(other_asset)
    elif 'parentIds' == key:
        if method == 'PATCH':
            other_asset.add_child(asset)
        elif method == 'DELETE':
            other_asset.remove_child(asset)
    elif 'connectedIds' == key:
        if method == 'PATCH':
            asset.add_connection(other_asset)
        elif method == 'DELETE':
            asset.remove_connection(other_asset)
    else:
        raise HTTPBadRequest({'key': 'is not recognized'})

    changed_assets = [asset] + asset.parents + asset.children
    return [_.serialize() for _ in changed_assets]


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
