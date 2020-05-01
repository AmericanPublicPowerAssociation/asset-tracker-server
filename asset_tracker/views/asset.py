from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..constants.asset import ASSET_TYPE_BY_CODE
from ..exceptions import DataValidationError
from ..macros.asset import RecordIdMirror
from ..routines.asset import (
    get_asset_by_id_json_dictionary,
    get_asset_dictionary_by_id,
    get_asset_feature_collection,
    get_assets_geojson_dictionary,
    get_viewable_assets,
    update_asset_connections,
    update_asset_geometries,
    update_assets)


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    assets = get_viewable_assets(request)
    return {
        'assetTypeByCode': ASSET_TYPE_BY_CODE,
        'assetById': get_asset_by_id_json_dictionary(assets),
        'assetsGeoJson': get_assets_geojson_dictionary(assets),
    }


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='PATCH')
def change_assets_json(request):
    params = request.json_body
    # TODO: Check whether user has edit privileges to specified assets
    try:
        asset_dictionary_by_id = get_asset_dictionary_by_id(params)
        asset_feature_collection = get_asset_feature_collection(params)
    except DataValidationError as e:
        raise HTTPBadRequest(e.args[0])

    db = request.db
    asset_id_mirror = RecordIdMirror()
    try:
        update_assets(db, asset_dictionary_by_id, asset_id_mirror)
        update_asset_connections(db, asset_dictionary_by_id, asset_id_mirror)
    except DataValidationError as e:
        raise HTTPBadRequest({'assets': e.args[0]})
    try:
        update_asset_geometries(db, asset_feature_collection, asset_id_mirror)
    except DataValidationError as e:
        raise HTTPBadRequest({'assetsGeoJson': e.args[0]})

    d = see_assets_json(request)
    del d['asset_type_by_code']
    return d
