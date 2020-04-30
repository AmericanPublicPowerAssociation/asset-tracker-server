import json
from cgi import FieldStorage

import shapely
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from shapely import wkt
from sqlalchemy.orm import selectinload
from ..constants.assets import ASSET_TYPES
from ..exceptions import DataValidationError
from ..routines.exporter import build_flat_dict_structure, validate_assets_df, get_extra_columns_df
from ..models import Asset, Bus, Connection, AssetTypeCode
from ..routines.geometry import get_bounding_box
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

import pandas as pd
import numpy as np


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
        'boundingBox': get_bounding_box(assets),
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


@view_config(
    route_name='assets.csv',
    renderer='json',
    request_method='PATCH')
def receive_assets_file(request):
    override_records = request.params.get('overwrite') == 'true'

    try:
        f = request.params['file']
    except KeyError:
        raise HTTPBadRequest({'file': 'is required'})
    if not isinstance(f, FieldStorage):
        raise HTTPBadRequest({'file': 'must be an upload'})

    def load_json(json_string):
        try:
          return json.loads(json_string)
        except json.decoder.JSONDecodeError:
          return json.loads(json_string.replace("'", '"'))

    try:
      validated_assets, errors = validate_assets_df(pd.read_csv(f.file, comment='#', converters={'connections': load_json}))
    except json.decoder.JSONDecodeError as e:
        raise HTTPBadRequest(str(e).strip())
    except pd.errors.ParserError as e:
        raise HTTPBadRequest(str(e).split(':')[-1].strip())

    if errors:
        raise HTTPBadRequest(errors)

    has_connections = 'connections' in validated_assets.columns
    has_wkt = 'wkt' in validated_assets.columns

    db = request.db

    extra_columns = get_extra_columns_df(validated_assets, [
        'id',
        'typeCode',
        'name',
        'connections',
        'wkt',
    ])
    for name, row in validated_assets.iterrows():
        asset = db.query(Asset).get(row['id'])
        if asset:
            if not override_records:
                continue
        else:
            asset = Asset(id=row['id'])

        asset.type_code = AssetTypeCode(row['typeCode'])
        asset.name = row['name']

        extra = {}
        for column in extra_columns:
            value = row[column]
            if isinstance(value, float) and np.isnan(value):
                continue
            extra[column] = value
        asset.attributes = extra

        if has_wkt:
            geometry = row['wkt']
            if not (isinstance(geometry, float) and np.isnan(geometry)):
                try:
                    asset.geometry = wkt.loads(geometry)
                except shapely.errors.WKTReadingError as e:
                    raise HTTPBadRequest(f'failed to parse ')

        db.add(asset)

    for name, row in validated_assets.iterrows():
        asset = db.query(Asset).get(row['id'])

        if has_connections:
            for connection in row['connections']:
                bus = db.query(Bus).get(connection['busId'])
                if not bus:
                    bus = Bus(id=connection['busId'])
                    db.add(bus)
                elif not override_records:
                    continue

                conn = db.query(Connection).get({"asset_id": asset.id, "bus_id": bus.id})

                if conn:
                    if not override_records:
                        continue
                    conn._attributes = connection['attributes']
                else:
                    conn = Connection(asset_id=asset.id, bus_id=bus.id, _attributes=connection['attributes'])
                    db.add(conn)

    try:
        db.flush()
    except Exception:
        db.rollback()

    return {
        'error': False
    }