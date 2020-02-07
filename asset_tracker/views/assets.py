import json
from os.path import dirname, join
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from ..constants import PACKAGE_FOLDER
from ..exceptions import DataValidationError
from ..routines import (
    get_asset_dictionaries,
    get_asset_feature_collection,
    update_asset_connections,
    update_asset_geometries,
    update_assets)


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    # db = request.db
    REPOSITORY_FOLDER = dirname(PACKAGE_FOLDER)
    DATASETS_FOLDER = join(REPOSITORY_FOLDER, 'datasets')
    assets_json_path = join(DATASETS_FOLDER, 'assets1.json')
    assets_geojson_path = join(DATASETS_FOLDER, 'assets1.geojson')
    assets_json_file = open(assets_json_path, 'rt')
    assets_geojson_file = open(assets_geojson_path, 'rt')
    return {
        # 'assetTypes':
        'assets': json.load(assets_json_file),
        'assetsGeoJson': json.load(assets_geojson_file),
        # 'boundingBox':
    }


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='PATCH')
def change_assets_json(request):
    params = request.json_body
    try:
        asset_dictionaries = get_asset_dictionaries(params)
        asset_feature_collection = get_asset_feature_collection(params)
    except DataValidationError as e:
        raise HTTPBadRequest(e.args[0])

    db = request.db
    asset_id_by_temporary_id = {}
    try:
        update_assets(
            db, asset_dictionaries, asset_id_by_temporary_id)
        update_asset_connections(
            db, asset_dictionaries, asset_id_by_temporary_id)
    except DataValidationError as e:
        raise HTTPBadRequest({'assets': e.args[0]})
    try:
        update_asset_geometries(
            db, asset_feature_collection, asset_id_by_temporary_id)
    except DataValidationError as e:
        raise HTTPBadRequest({'assetsGeoJson': e.args[0]})

    return {}
