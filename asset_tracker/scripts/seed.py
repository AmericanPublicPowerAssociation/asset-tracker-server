import json
import optparse
import sys
import textwrap
from copy import deepcopy

import shapely
from shapely import wkt
from shapely.geometry import mapping as get_geojson_dictionary

from pyramid.paster import bootstrap

from asset_tracker.models import Asset, Bus, Connection
from asset_tracker.models.asset import LineType, AssetTypeCode


def export_json(db, export_file, indent=2):
    assets = db.query(Asset).filter_by(is_deleted=False).all()
    buses = db.query(Bus).all()
    connections = db.query(Connection).all()
    line_types = db.query(LineType).all()

    db_json = {
        'assets': [],
        'buses': [],
        'connections': [],
        'line_types': []
    }
    for asset in assets:
        db_json['assets'].append({
            'typeCode': asset.type_code.value,
            'name': asset.name,
            'attributes': asset.attributes,
            'id': asset.id,
            'wkt': asset.geometry.wkt
        })

    for bus in buses:
        db_json['buses'].append({
            'id': bus.id
        })

    for connection in connections:
        db_json['connections'].append({
            'asset_id': connection.asset_id,
            'asset_vertex_index': connection.asset_vertex_index,
            'bus_id': connection.bus_id,
            'attributes': connection.attributes
        })

    for line_type in line_types:
        db_json['line_types'].append({
            'id': line_type.id,
            'attributes': line_type.attributes
        })

    if export_file:
        with open(export_file, 'w') as f:
            json.dump(db_json, f, indent=indent, sort_keys=True)
    else:
        print(json.dumps(db_json, indent=indent, sort_keys=True))


def generate_connections(json_data, asset_id):
    asset_connections =  list(filter(lambda c: c['asset_id'] == asset_id, json_data['connections']))
    connections = []
    hashes = []
    for connection in reversed(asset_connections):
        connection_obj = Connection(bus_id=connection['bus_id'], _attributes=deepcopy(connection['attributes']))
        connection_obj.asset_vertex_index = connection['asset_vertex_index']
        hash = f'{connection["asset_id"]}{connection["bus_id"]}'
        if hash not in hashes:
            connections.append(connection_obj)
            print(connection_obj.attributes)
            hashes.append(hash)
        else:
            print(hash)

    return connections


def remove_all_entries(db):
    db.query(Asset).delete()
    db.query(Bus).delete()
    db.query(Connection).delete()
    db.query(LineType).delete()


def import_json(db, file, utility_id):
    with open(file, 'r') as f:
        json_data = json.load(f)

        remove_all_entries(db)

        for asset in json_data['assets']:
            new_asset = Asset(
                id=asset['id'],
                name=asset['name'],
                utility_id=utility_id)
            new_asset.type_code = AssetTypeCode(asset['typeCode'])
            new_asset.attributes = asset['attributes']

            try:
                new_asset.geometry = wkt.loads(asset['wkt'])
            except shapely.errors.WKTReadingError:
                print(f'asset(id={new_asset.id}) invalid geometry')

            connections = generate_connections(json_data, asset['id'])

            new_asset.connections = connections
            db.add(new_asset)

        for bus in json_data['buses']:
            new_bus = Bus(id=bus['id'])
            db.add(new_bus)

        for line_type in json_data['line_types']:
            new_line_type = LineType(id=line_type['id'])
            new_line_type.attributes = line_type['attributes']

            db.add(new_line_type)


def init():
    description = """\
    Seed db with examples:
    'seed_db deployment.ini'
    """
    usage = "usage: %prog config_uri"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description))

    options, args = parser.parse_args(sys.argv[1:])
    if len(args) < 1:
        print('You must provide the subcommands: import or export')
        return 2

    if args[0] not in ['import', 'export']:
        print('Subcommand no supported')
        return 2

    if not len(args) >= 2:
        print('You must provide at configuration file')
        return 2

    subcommand = args[0]
    config_uri = args[1]
    export_file = args[2] if len(args) > 2 else ''
    utility_id = args[3]

    with bootstrap(config_uri) as env:
        with env['request'].tm:

            db = env['request'].db

            if subcommand == 'export':
                export_json(db, export_file)

            elif subcommand == 'import':
                if export_file == 'blank':
                    remove_all_entries(db)
                else:
                    import_json(db, export_file, utility_id)
