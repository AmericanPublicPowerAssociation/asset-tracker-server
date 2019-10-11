import io

import networkx as nx
import numpy as np
import pandas as pd
import shapely.wkt as wkt
from cgi import FieldStorage
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInsufficientStorage,
    HTTPNotFound)
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import desc
from sqlalchemy.orm import selectinload

from asset_tracker.routines.opendss import (BUS, GENERATOR, TRANSFORMER, LINE, LOAD, METER, node_existence,
                                            create_node, create_connection, Circuit, comment)
from ..constants import ASSET_TYPES
from ..exceptions import DatabaseRecordError
from ..macros.text import normalize_text
from ..models import Asset, LogEvent, Task
from ..models.log import log_event
from ..routines.geometry import get_bounding_box
from ..routines.table import (
    prepare_column)
from ..utils.data import (
    build_flat_dict_structure,
    get_extra_columns_df,
    transform_array_to_csv)
from ..validators.assets import validate_assets_df


@view_config(
    route_name='assets_kit.json',
    renderer='json',
    request_method='GET')
def see_assets_kit_json(request):
    valid_columns = {
        'typeid': Asset.type_id,
        'name': Asset.name
    }
    db = request.db
    try:
        key = request.GET['column']
        column = valid_columns[key]
        query = (
            desc(column) if request.GET['desc'].lower() == 'true'
            else column)
        assets = db.query(Asset).options(
            selectinload(Asset.parents),
            selectinload(Asset.children),
            selectinload(Asset.connections)
        ).order_by(query).all()
    except KeyError:
        assets = db.query(Asset).options(
            selectinload(Asset.parents),
            selectinload(Asset.children),
            selectinload(Asset.connections),
        ).all()
    # !!! Filter assets by utility ids to which user has read access
    return {
        'assetTypes': ASSET_TYPES,
        'assets': [_.get_json_d() for _ in assets],
        'boundingBox': get_bounding_box(assets),
    }


@view_config(
    route_name='assets_metrics.json',
    renderer='json',
    request_method='GET')
def see_assets_metrics_json(request):
    db = request.db

    asset_ids = Asset.get_readable_ids(request)
    asset_count = len(asset_ids)
    assets = db.query(Asset).filter(Asset.id.in_(asset_ids)).all()

    meter_count = len([
        _ for _ in assets if
        _.primary_type_id == 'm'])

    missing_location_count = len([
        _ for _ in assets if
        _.can_have_location and
        not _.location])

    missing_connection_count = len([
        _ for _ in assets if
        _.can_have_connection and
        not _.connections])

    # !!! Separate into asset-report-risks
    missing_vendor_name_count = len([
        _ for _ in assets if
        not (_.attributes or {}).get('vendorName')])

    # !!! Separate into asset-report-risks
    missing_product_name_count = len([
        _ for _ in assets if
        _.can_be_mass_produced and
        not (_.attributes or {}).get('productName')])

    missing_line_count = len([
        _ for _ in assets if _.primary_type_id == 'p'
        and not _.has_parent_type_id('l')])

    return {
        'assetCount': asset_count,
        'meterCount': meter_count,
        'missingLocationCount': missing_location_count,
        'missingConnectionCount': missing_connection_count,
        'missingVendorNameCount': missing_vendor_name_count,
        'missingProductNameCount': missing_product_name_count,
        'missingLineCount': missing_line_count,
    }


@view_config(
    route_name='assets.csv',
    request_method='GET')
def see_assets_csv(request):
    db = request.db
    assets = db.query(Asset).options(
        selectinload(Asset.parents),
        selectinload(Asset.children),
        selectinload(Asset.connections),
    ).all()
    order_columns = [
        'id', 'utilityId', 'typeId', 'name',
        'vendorName', 'productName', 'productVersion',
        'KV', 'KW', 'KWH',
        'location', 'wkt',
        'parentIds', 'childIds', 'connectedIds',
    ]
    csv = ','.join(order_columns)

    if len(assets) > 0:
        assets = [build_flat_dict_structure(_) for _ in assets]
        data = pd.DataFrame(assets)
        transform_array_to_csv(data, 'location')
        transform_array_to_csv(data, 'childIds', sep=' ')
        transform_array_to_csv(data, 'parentIds', sep=' ')
        transform_array_to_csv(data, 'connectedIds', sep=' ')
        csv = data[order_columns].to_csv(index=False)

    log_event(request, LogEvent.export_assets_csv, {})
    return Response(
        body=csv,
        status=200,
        content_type='text/csv',
        content_disposition='attachment')


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

    log_event(request, LogEvent.add_asset, {'assetId': asset.id})
    return asset.get_json_d()


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='PATCH')
def change_asset_json(request):
    matchdict = request.matchdict
    params = dict(request.json_body)

    id = matchdict['id']
    db = request.db
    asset = db.query(Asset).options(
        selectinload(Asset.parents),
        selectinload(Asset.children),
        selectinload(Asset.connections),
    ).get(id)
    if not asset:
        raise HTTPNotFound({'id': 'does not exist'})
    changed_assets = [asset]

    utility_id = asset.utility_id

    # !!! Check whether user can update this asset

    db = request.db
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
        if not asset.can_have_location:
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

    log_event(request, LogEvent.change_asset, dict({
        'assetId': asset.id,
    }, **dict(request.json_body)))
    return [_.get_json_d() for _ in changed_assets]


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
    asset = db.query(Asset).options(
        selectinload(Asset.parents),
        selectinload(Asset.children),
        selectinload(Asset.connections),
    ).get(id)
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
    log_event(request, LogEvent.change_asset_relation, {
        'assetId': matchdict['id'],
        'otherAssetId': matchdict['otherId'],
        'key': matchdict['key'],
    })
    return [_.get_json_d() for _ in changed_assets]


@view_config(
    route_name='asset.json',
    renderer='json',
    request_method='DELETE')
def drop_asset_json(request):
    # log(request, LogEvent.drop_asset, {'id': asset.id})
    return {}


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
    # try:
    # except FileUploadError as e:

    # !!! raise exception here
    validated_assets, errors = validate_assets_df(pd.read_csv(f.file))

    if errors:
        raise HTTPBadRequest(errors)

    prepare_column(validated_assets, 'location', cast=float)
    prepare_column(validated_assets, 'childIds', separator=' ')
    prepare_column(validated_assets, 'parentIds', separator=' ')
    prepare_column(validated_assets, 'connectedIds', separator=' ')

    db = request.db

    # TODO: move this logic to model or helper function
    extra_columns = get_extra_columns_df(validated_assets, [
        'id',
        'utilityId',
        'typeId',
        'name',
        'parentIds',
        'childIds',
        'connectedIds',
        'wkt',
        'location',
        'geometry',
    ])
    for name, row in validated_assets.iterrows():
        asset = db.query(Asset).get(row['id'])
        if asset:
            if not override_records:
                continue
        else:
            asset = Asset(id=row['id'])

        asset.utility_id = row['utilityId']
        asset.type_id = row['typeId']
        asset.name = row['name']
        if len(row['location']) == 2:
            asset.location = row['location']
        extra = {}
        for column in extra_columns:
            value = row[column]
            if isinstance(value, float) and np.isnan(value):
                continue
            extra[column] = value

        asset.attributes = extra
        geometry = row['wkt']
        if not (isinstance(geometry, float) and np.isnan(geometry)):
            asset.geometry = wkt.loads(geometry)

        db.add(asset)

    for name, row in validated_assets.iterrows():
        asset = db.query(Asset).get(row['id'])

        for child_id in row['childIds']:
            child = db.query(Asset).get(child_id)
            if child:
                asset.add_child(child)

        for connected_id in row['connectedIds']:
            connected = db.query(Asset).get(connected_id)
            if connected:
                asset.add_connection(connected)

    try:
        db.flush()
    except Exception:
        db.rollback()

    log_event(request, LogEvent.import_assets_csv, {})

    return {
        'error': False
    }


@view_config(
    route_name='asset_tasks.json',
    renderer='json',
    request_method='GET')
def see_asset_tasks_json(request):
    matchdict = request.matchdict
    # params = request.params
    id = matchdict['id']
    db = request.db
    # !!! Check if user can view asset
    # !!! Restrict view to tasks that user can view
    tasks = db.query(Task).filter(Task.asset_id == id).all()
    return [_.get_json_d() for _ in tasks]


@view_config(
    route_name='assets.dss',
    request_method='GET')
def export_assets_to_dss(request):
    db = request.db
    G = nx.Graph()

    ELEMENTS = {
        BUS:  {'title': 'Buses', 'assets': []},
        GENERATOR:  {'title': 'Generators', 'assets': []},
        TRANSFORMER:  {'title': 'Transformers', 'assets': []},
        LINE: {'title': 'Lines', 'assets': []},
        LOAD:  {'title': 'Loads', 'assets': []},
        METER:  {'title': 'Meters', 'assets': []},
    }

    EXPORT_ASSETS = [METER, LINE, GENERATOR]

    for asset in db.query(Asset).all():
        if asset.type_id[0] in EXPORT_ASSETS:
            current_node = node_existence(asset.id, graph=G)
            if not current_node:
                current_node = create_node(asset, index=ELEMENTS, graph=G)

            for inner_asset in asset.connections:
                if inner_asset.type_id in EXPORT_ASSETS:
                    inner_node = node_existence(inner_asset.id, graph=G)
                    if not inner_node:
                        inner_node = create_node(inner_asset, index=ELEMENTS, graph=G)

                    create_connection(current_node, inner_node, index=ELEMENTS, graph=G)


    f = io.StringIO()

    if len(ELEMENTS[GENERATOR]['assets']) == 0:
        warning_comment = comment('WARNING: No GENERATORS exist')
        f.write(f'{warning_comment}\n')

    f.write('clear\n')
    circuit = Circuit('SimpleCircuit')
    f.write(f'{circuit}\n')
    for asset_type, element in ELEMENTS.items():
        f.write(f'{comment(element["title"])}\n')

        for asset in element["assets"]:
            f.write(f'{asset}\n')

    f.write('\nmakebuslist\nsolve\n')

    return Response(
        body=f.getvalue(),
        status=200,
        content_type='text/plain',
        content_disposition='attachment')


def validate_name(db, name, utility_id, id=None):
    name = normalize_text(name)
    if not name:
        raise HTTPBadRequest({'name': 'cannot be empty'})
    duplicate_query = db.query(Asset).filter(
        Asset.utility_id == utility_id,
        Asset.name.ilike(name))
    if id:
        duplicate_query = duplicate_query.filter(Asset.id != id)
    if duplicate_query.count():
        raise HTTPBadRequest({'name': 'must be unique within utility'})
    return name
