import io

import networkx as nx
import numpy as np
import pandas as pd
import shapely.wkt as wkt
from cgi import FieldStorage

from networkx.drawing.nx_pydot import write_dot
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInsufficientStorage,
    HTTPNotFound)
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy import desc
from sqlalchemy.orm import selectinload

from asset_tracker.models.asset import asset_connection
from asset_tracker.routines.opendss import (BUS, GENERATOR, TRANSFORMER, LINE, LOAD, METER, node_existence,
                                            create_node, create_connection, Circuit, comment, create_bus, connect,
                                            get_node, DEFAULT_SOURCE_BUS, LineCode, LINECODE, SWITCH, STORAGE,
                                            POWERQUALITY, BASIC_LC)
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

    instructions = '\n'.join([
        '# Only keep the required columns: Id, Name and typeId to create new elements.',
        '# If you want to override the information of an element please reference the element through the required columns.',
        '# Then and add any other column to be changed, such as: "utilityId", "vendorName", "productName", "productVersion", "KV", "KW", "KWH", "location", "wkt", "childIds", "connectedIds".',
        '# And activate the override checkbox in the uploader.',
    ])

    columns = ','.join(order_columns)
    csv = f'{instructions}\n{columns}'

    if len(assets) > 0:
        assets = [build_flat_dict_structure(_) for _ in assets]
        data = pd.DataFrame(assets)
        transform_array_to_csv(data, 'location')
        transform_array_to_csv(data, 'childIds', sep=' ')
        transform_array_to_csv(data, 'parentIds', sep=' ')
        transform_array_to_csv(data, 'connectedIds', sep=' ')
        csv_data = data[order_columns].to_csv(index=False)
        csv = f'{instructions}\n{csv_data}'

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
    route_name='shape.csv',
    renderer='json',
    request_method='POST')
def receive_asset_shape(request):
    asset_id = request.matchdict['asset']
    db = request.db

    asset = db.query(Asset).get(asset_id)
    if not asset:
        raise HTTPNotFound({'asset': 'doensn\'t exists'})

    try:
        f = request.params['file']
    except KeyError:
        raise HTTPBadRequest({'file': 'is required'})
    if not isinstance(f, FieldStorage):
        raise HTTPBadRequest({'file': 'must be an upload'})

    df = pd.read_csv(f.file, comment='#')
    df = df.dropna(how='all')
    if len(df.columns) > 0:
        df = df.select_dtypes(include=["float", 'int'])
        asset.shape = df.to_dict()

        return {
            'error': False
        }

    raise HTTPBadRequest({'file': ' has not content'})

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
    validated_assets, errors = validate_assets_df(pd.read_csv(f.file, comment='#'))

    if errors:
        raise HTTPBadRequest(errors)

    has_utility_id = 'utilityId' in validated_assets.columns
    has_parent_ids = 'parentIds' in validated_assets.columns
    has_child_ids = 'childIds' in validated_assets.columns
    has_connected_ids = 'connectedIds' in validated_assets.columns
    has_wkt = 'wkt' in validated_assets.columns
    has_location = 'location' in validated_assets.columns

    if has_parent_ids:
        prepare_column(validated_assets, 'parentIds', separator=' ')
    if has_location:
        prepare_column(validated_assets, 'location', cast=float)
    if has_child_ids:
        prepare_column(validated_assets, 'childIds', separator=' ')
    if has_connected_ids:
        prepare_column(validated_assets, 'connectedIds', separator=' ')

    db = request.db

    # TODO: move this logic to model or helper function
    extra_columns = get_extra_columns_df(validated_assets, [
        'id',
        'typeId',
        'name',
        'utilityId',
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
            compound_key = db.query(Asset).filter(Asset.name == row.get('name',''),
                                                  Asset.utility_id == row.get('utilityId', ''))
            if compound_key.count() > 0:
                continue

            asset = Asset(id=row['id'])

        asset.type_id = row['typeId']
        asset.name = row['name']

        if has_utility_id:
            asset.utility_id = row.get('utilityId', '')

        if has_location and len(row['location']) == 2:
            asset.location = row['location']

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
                asset.geometry = wkt.loads(geometry)

        db.add(asset)

    for name, row in validated_assets.iterrows():
        asset = db.query(Asset).get(row['id'])
        if not asset:
            continue
            
        if has_child_ids:
            for child_id in row['childIds']:
                child = db.query(Asset).get(child_id)
                if child:
                    asset.add_child(child)

        if has_connected_ids:
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
        # BUS:  {'title': 'Buses', 'assets': []},
        GENERATOR:  {'title': 'Generators', 'assets': []},
        TRANSFORMER:  {'title': 'Transformers', 'assets': []},
        LINECODE: {'title': 'Line Codes', 'assets': [BASIC_LC]},
        LINE: {'title': 'Lines', 'assets': []},
        METER:  {'title': 'Loads', 'assets': []},
        SWITCH: {'title': 'Switch', 'assets': []},
        STORAGE: {'title': 'Storage', 'assets': []},
        POWERQUALITY: {'title': 'Power Quality', 'assets': []},
    }

    EXPORT_ASSETS = [LINE, METER, GENERATOR, SWITCH, STORAGE, TRANSFORMER, POWERQUALITY]

    circuit = Circuit('SimpleCircuit')
    G.add_node(circuit.name, instance=circuit, translate=circuit)
    circuit.bus = create_bus(circuit, name=DEFAULT_SOURCE_BUS)

    # Build Graph
    for asset in db.query(Asset).all():
        # Connect Circuit to Generators
        if asset.type_id[0] is GENERATOR:
            current_node = get_node(asset, G, ELEMENTS)
            create_connection(circuit, current_node, graph=G)

        # Generate all allowed assets
        if asset.type_id[0] in EXPORT_ASSETS:
            current_node = get_node(asset, G, ELEMENTS)
            for inner_asset in asset.connections:
                if inner_asset.type_id in EXPORT_ASSETS:
                    inner_node = get_node(inner_asset, G, ELEMENTS)
                    print(current_node)
                    print(inner_node)
                    create_connection(current_node, inner_node, graph=G)

    # Make connections
    connections = []
    for node in nx.dfs_preorder_nodes(G, source=circuit.name):
        for id1, id2 in G.edges(node):
            identificator = ' '.join(map(str, sorted([id1, id2])))

            E1 = node_existence(id1, G)
            E2 = node_existence(id2, G)
            if identificator not in connections:
                connected = connect(E1, E2, ELEMENTS)
                print(f'{id1} => {id2} ({connected})')
                if connected:
                    connections.append(identificator)

    f = io.StringIO()

    if len(ELEMENTS[GENERATOR]['assets']) == 0:
        warning_comment = comment('WARNING: No GENERATORS exist')
        f.write(f'{warning_comment}\n')

    f.write('clear\n')

    f.write(f'{circuit}\n')
    for asset_type, element in ELEMENTS.items():
        f.write(f'\n{comment(element["title"])}\n')

        for asset in element["assets"]:
            f.write(f'{asset}\n')

    f.write('Set voltagebases=[20]\n'
            'CalcVoltageBases\n\n'
            'solve\n'
            'Show Powers kva Elements\n'
            'Show Voltage LL\n')

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
