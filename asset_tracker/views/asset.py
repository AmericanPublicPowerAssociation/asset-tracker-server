import json
import numpy as np
import pandas as pd
import shapely
from appa_auth_consumer.constants import ROLE_MEMBER, ROLE_SPECTATOR
from cgi import FieldStorage
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from shapely import wkt

from ..constants.asset import ASSET_TYPE_BY_CODE
from ..exceptions import DataValidationError
from ..macros.database import RecordIdMirror
from ..models import Asset, Bus, Connection, AssetTypeCode
from ..routines import get_utility_ids
from ..routines.asset import (
    get_asset_dictionary_by_id,
    get_asset_feature_collection,
    get_assets_geojson_dictionary,
    update_asset_connections,
    update_asset_geometries,
    update_assets)
# TODO: Rename exporter module to something else
from ..routines.exporter import (
    build_flat_dict_structure, validate_assets_df, get_extra_columns_df)
from ..routines.geometry import get_bounding_box


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    assets = Asset.get_viewable_query(request, with_connections=True).all()
    return {
        'assetTypeByCode': ASSET_TYPE_BY_CODE,
        'assetById': {
            _.id: _.get_json_dictionary_without_id() for _ in assets},
        'assetsGeoJson': get_assets_geojson_dictionary(assets),
        'boundingBox': get_bounding_box(assets),
    }


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='PATCH')
def change_assets_json(request):
    params = request.json_body
    try:
        asset_dictionary_by_id = get_asset_dictionary_by_id(params)
        asset_feature_collection = get_asset_feature_collection(params)
    except DataValidationError as e:
        raise HTTPBadRequest(e.args[0])
    # print(asset_dictionary_by_id)

    session = request.session
    viewable_utility_ids = get_utility_ids(session, ROLE_SPECTATOR)
    editable_utility_ids = get_utility_ids(session, ROLE_MEMBER)
    asset_dictionary_by_id = {
        k: v for k, v in asset_dictionary_by_id.items()
        if v['utilityId'] in viewable_utility_ids}

    db = request.db
    asset_id_mirror = RecordIdMirror()
    try:
        update_assets(
            db,
            asset_dictionary_by_id,
            asset_id_mirror,
            editable_utility_ids)
        update_asset_connections(
            db,
            asset_dictionary_by_id,
            asset_id_mirror,
            editable_utility_ids)
    except DataValidationError as e:
        raise HTTPBadRequest({'assets': e.args[0]})
    try:
        update_asset_geometries(
            db,
            asset_feature_collection,
            asset_id_mirror,
            editable_utility_ids)
    except DataValidationError as e:
        raise HTTPBadRequest({'assetsGeoJson': e.args[0]})

    d = see_assets_json(request)
    d['assetIdById'] = asset_id_mirror.get_json_dictionary()
    del d['assetTypeByCode']
    return d


@view_config(
    route_name='assets.csv',
    request_method='GET')
def see_assets_csv(request):
    # TODO: Review and clean
    assets = Asset.get_viewable_query(request, with_connections=True).all()

    base_columns = {'id', 'typeCode', 'name', 'wkt', 'connections'}
    columns = ','.join(base_columns)
    csv = columns

    if len(assets) > 0:
        flat_assets = []
        columns = set()
        for asset in assets:
            if asset.geometry:
                flat_asset = build_flat_dict_structure(asset)
                flat_assets.append(flat_asset)
                headers = set(flat_asset.keys())
                columns.update(headers - base_columns)
        '''
        order_columns = [
            'id', 'typeCode', 'name', *sorted(columns), 'wkt', 'connections']
        '''
        order_columns = [
            'id', 'typeCode', 'name', *sorted(columns), 'wkt']

        for asset in flat_assets:
            headers = set(asset.keys())
            for missing_col in (columns - headers):
                asset[missing_col] = None

        data = pd.DataFrame(flat_assets)
        csv_data = data[order_columns].to_csv(index=False, )
        csv = csv_data

    return Response(
        body=csv,
        status=200,
        content_type='text/csv',
        content_disposition='attachment')


@view_config(
    route_name='assets.csv',
    renderer='json',
    request_method='PATCH')
def change_assets_csv(request):
    # TODO: Review and clean
    override_records = request.params.get('overwrite') == 'true'

    try:
        f = request.params['file']
    except KeyError:
        raise HTTPBadRequest(
            headers={'content_type': 'application/json'},
            body=json.dumps({
                'errors':
                    {'file': 'is required'},
                }))
    if not isinstance(f, FieldStorage):
        raise HTTPBadRequest(
            headers={'content_type': 'application/json'},
            body=json.dumps({
                'errors':
                    {'file': 'must be an upload'},
                }))

    def load_json(json_string):
        try:
            return json.loads(json_string)
        except json.decoder.JSONDecodeError:
            return json.loads(json_string.replace("'", '"'))

    try:
        fileName = f.filename
        if '.xls' in fileName or '.xlsx' in fileName:
            validated_assets, errors = validate_assets_df(pd.read_excel(
                f.file, comment='#', converters={'connections': load_json}))
        elif '.ods' in fileName:
            validated_assets, errors = validate_assets_df(pd.read_excel(
                f.file, comment='#', converters={'connections': load_json},
                engine="odf"))
        elif '.csv' in fileName:
            validated_assets, errors = validate_assets_df(pd.read_csv(
                f.file, comment='#', converters={'connections': load_json}))
        else:
            raise HTTPBadRequest(
                headers={'content_type': 'application/json'},
                body=json.dumps({
                    'errors':
                        {'file': 'file format is not supported.'},
                    }))
    except json.decoder.JSONDecodeError as e:
        raise HTTPBadRequest(
            headers={'content_type': 'application/json'},
            body=json.dumps({
                'errors':
                    {'file': str(e).strip()},
                }))

    except pd.errors.ParserError as e:
        raise HTTPBadRequest(
            headers={'content_type': 'application/json'},
            body=json.dumps({
                'errors':
                    {'file': str(e).split(':')[-1].strip()},
                }))

    if errors:
        raise HTTPBadRequest(
            headers={'content_type': 'application/json'},
            body=json.dumps({
                'errors':
                    {'file': errors},
                }))

    # has_connections = 'connections' in validated_assets.columns
    has_connections = False
    has_wkt = 'wkt' in validated_assets.columns

    db = request.db

    extra_columns = get_extra_columns_df(validated_assets, [
        'id',
        'typeCode',
        'name',
        'connections',
        'wkt',
    ])

    save_errors = {}
    for name, row in validated_assets.iterrows():
        asset_id = row['id']
        asset_save_errors = {}
        asset = db.query(Asset).get(row['id'])
        if asset:
            if not override_records:
                asset_save_errors['overwrite'] = 'Asset exist - \
                    Check overwrite existing records.'
        else:
            asset = Asset(id=row['id'])

        try:
            asset.type_code = AssetTypeCode(row['typeCode'])
        except ValueError as e:
            asset_save_errors['typeCode'] = e.args[0]

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
                except shapely.errors.WKTReadingError:
                    # raise HTTPBadRequest(f'failed to parse ')
                    asset_save_errors['wkt'] = 'invalid geometry'

        if len(asset_save_errors):
            save_errors[asset_id] = asset_save_errors
            continue
        else:
            asset.name = row['name']
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

                conn = db.query(Connection).get({
                    'asset_id': asset.id, 'bus_id': bus.id})

                if conn:
                    if not override_records:
                        continue
                    conn._attributes = connection['attributes']
                else:
                    conn = Connection(asset_id=asset.id, bus_id=bus.id)
                    conn.attributes = connection['attributes']
                    db.add(conn)

    try:
        db.flush()
    except Exception:
        db.rollback()

    return {
        'errors': (
            {'save_errors': save_errors} if len(save_errors) else False)
    }
