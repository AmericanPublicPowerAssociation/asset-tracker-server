from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm import selectinload
import pandas as pd
from ..constants.assets import ASSET_TYPES
from ..exceptions import DataValidationError
from ..macros.exporter import build_flat_dict_structure
from ..models import Asset
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
    return {
        'assetTypes': ASSET_TYPES,
        'assets': get_assets_json_list(assets),
        'assetsGeoJson': get_assets_geojson_dictionary(assets),
        # 'boundingBox':
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


@view_config(
    route_name='assets.csv',
    request_method='GET')
def see_assets_csv(request):
    db = request.db
    assets = db.query(Asset).options(
        selectinload(Asset.connections),
    ).all()

    instructions = '\n'.join([
        '# Only keep the required columns: Id, Name and typeId to create new elements.',
        '# If you want to override the information of an element please reference the element through the required columns.',
        '# Then and add any other column to be changed, such as: "utilityId", "vendorName", "productName", "productVersion", "KV", "KW", "KWH", "location", "wkt", "childIds", "connectedIds".',
        '# And activate the override checkbox in the uploader.',
    ])

    base_columns = {'id', 'typeCode', 'name', 'wkt', 'connections'}
    columns = ','.join(base_columns)
    csv = f'{instructions}\n{columns}'

    if len(assets) > 0:
        flat_assets = []
        columns = set()
        for asset in assets:
            flat_asset = build_flat_dict_structure(asset)
            print(flat_asset)
            flat_assets.append(flat_asset)
            headers = set(flat_asset.keys())
            columns.update(headers - base_columns)

        order_columns = ['id', 'typeCode', 'name', *sorted(columns), 'wkt', 'connections']

        for asset in flat_assets:
            headers = set(asset.keys())
            for missing_col in (columns - headers):
                asset[missing_col] = None

        data = pd.DataFrame(flat_assets)
        csv_data = data[order_columns].to_csv(index=False, )
        csv = f'{instructions}\n{csv_data}'

    return Response(
        body=csv,
        status=200,
        content_type='text/csv',
        content_disposition='attachment')