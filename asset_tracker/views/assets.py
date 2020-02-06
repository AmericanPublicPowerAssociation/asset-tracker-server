import json
from os.path import dirname, join
from pyramid.view import view_config

from ..constants import PACKAGE_FOLDER
from ..models import Asset


@view_config(
    route_name='assetsKit.json',
    renderer='json',
    request_method='GET')
def see_assets_kit_json(request):
    db = request.db
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
    return {}
