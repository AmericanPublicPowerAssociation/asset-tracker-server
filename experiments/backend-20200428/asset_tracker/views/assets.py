from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..constants.assets import ASSET_TYPES
from ..exceptions import DataValidationError
from ..routines.assets import (
    RecordIdMirror,
    get_asset_dictionaries,
    get_asset_feature_collection,
    get_assets_geojson_dictionary,
    get_assets_json_list,
    get_viewable_assets,
    update_asset_connections,
    update_asset_geometries,
    update_assets)


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    db = request.db
    assets = get_viewable_assets(db)
    '''
    return {
        'assetTypes': ASSET_TYPES,
        'assets': get_assets_json_list(assets),
        'assetsGeoJson': get_assets_geojson_dictionary(assets),
        # 'boundingBox':
    }
    '''
    return {
        'assetTypeByCode': {},
        ''
    }


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='PATCH')
def change_assets_json(request):
    params = request.json_body
    # TODO: Check whether user has edit privileges to specified assets
    try:
        asset_dictionaries = get_asset_dictionaries(params)
        asset_feature_collection = get_asset_feature_collection(params)
    except DataValidationError as e:
        raise HTTPBadRequest(e.args[0])

    db = request.db
    asset_id_mirror = RecordIdMirror()
    try:
        update_assets(db, asset_dictionaries, asset_id_mirror)
        update_asset_connections(db, asset_dictionaries, asset_id_mirror)
    except DataValidationError as e:
        raise HTTPBadRequest({'assets': e.args[0]})
    try:
        update_asset_geometries(db, asset_feature_collection, asset_id_mirror)
    except DataValidationError as e:
        raise HTTPBadRequest({'assetsGeoJson': e.args[0]})

    assets = get_viewable_assets(db)
    return {
        'assets': get_assets_json_list(assets),
        'assetsGeoJson': get_assets_geojson_dictionary(assets),
    }
