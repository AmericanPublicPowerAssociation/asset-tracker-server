from shapely.geometry import shape

from ..constants.assets import ASSET_TYPES
from ..exceptions import DataValidationError
from ..models import Asset, AssetTypeCode, Bus, Connection


class RecordIdMirror(object):

    def __init__(self):
        self.record_id_by_temporary_id = {}

    def get(self, record_id):
        record_id = str(record_id)
        return self.record_id_by_temporary_id.get(record_id, record_id)

    def set(self, temporary_id, record_id):
        temporary_id = str(temporary_id)
        record_id = str(record_id)
        self.record_id_by_temporary_id[temporary_id] = record_id
        return record_id


def absorb_asset_types(delta_asset_types):
    asset_type_by_code = {_['code']: _ for _ in ASSET_TYPES}
    for delta_asset_type in delta_asset_types:
        asset_type = asset_type_by_code[delta_asset_type['code']]
        for key in [
            'assetAttributes',
            'connectionAttributes',
        ]:
            delta_values = delta_asset_type.get(key, [])
            if not delta_values:
                continue
            asset_type[key] = asset_type.get(key, []) + delta_values


def get_assets_json_list(assets):
    return [_.get_json_dictionary() for _ in assets]


def get_assets_geojson_dictionary(assets):
    features = []
    for asset in assets:
        try:
            feature = asset.get_geojson_feature()
        except AttributeError:
            continue
        features.append(feature)
    return {
        'type': 'FeatureCollection',
        'features': features,
    }


def update_assets(db, asset_dictionaries, asset_id_mirror):
    error_by_index = {}

    for index, asset_dictionary in enumerate(asset_dictionaries):
        try:
            asset_id = get_asset_id(asset_dictionary)
            asset_type_code = get_asset_type_code(asset_dictionary)
            asset_name = get_asset_name(asset_dictionary)
            asset_attributes = get_asset_attributes(asset_dictionary)
        except DataValidationError as e:
            error_by_index[index] = e.args[0]
            continue

        asset_id = asset_id_mirror.get(asset_id)
        asset = db.query(Asset).get(asset_id)
        if not asset:
            asset = Asset.make_unique_record(db)
            asset_id = asset_id_mirror.set(asset_id, asset.id)

        asset.type_code = asset_type_code
        asset.name = asset_name
        asset.attributes = asset_attributes
        db.add(asset)

    if error_by_index:
        raise DataValidationError(error_by_index)
    db.flush()
    print(db.query(Asset).all())


def update_asset_connections(db, asset_dictionaries, asset_id_mirror):
    error_by_index = {}
    bus_id_mirror = RecordIdMirror()

    for index, asset_dictionary in enumerate(asset_dictionaries):
        try:
            asset_id = get_asset_id(asset_dictionary)
            connection_dictionaries = get_asset_connections(asset_dictionary)
        except DataValidationError as e:
            error_by_index[index] = e.args[0]
            continue

        asset_id = asset_id_mirror.get(asset_id)
        asset = db.query(Asset).get(asset_id)

        connections = []
        for connection_dictionary in connection_dictionaries:
            bus_id = get_bus_id(connection_dictionary)
            bus_id = bus_id_mirror.get(bus_id)
            bus = db.query(Bus).get(bus_id)
            if not bus:
                bus = Bus.make_unique_record(db)
                bus_id = bus_id_mirror.set(bus_id, bus.id)
            db.add(bus)
            connection = db.query(Connection).get({
                'asset_id': asset_id, 'bus_id': bus_id})
            if not connection:
                connection = Connection(bus_id=bus_id)
                connection.attributes = connection_dictionary.get(
                    'attributes', {})
            connections.append(connection)
        asset.connections = connections

    if error_by_index:
        raise DataValidationError(error_by_index)
    db.flush()


def update_asset_geometries(db, asset_feature_collection, asset_id_mirror):
    error_by_index = {}
    asset_features = asset_feature_collection['features']

    for index, asset_feature in enumerate(asset_features):
        try:
            asset_id = get_asset_feature_id(asset_feature)
            asset_geometry = get_asset_feature_geometry(asset_feature)
        except DataValidationError as e:
            error_by_index[index] = e.args[0]
            continue

        asset_id = asset_id_mirror.get(asset_id)
        asset = db.query(Asset).get(asset_id)
        asset.geometry = asset_geometry
        db.add(asset)

    if error_by_index:
        raise DataValidationError(error_by_index)
    db.flush()


def get_asset_dictionaries(params):
    asset_dictionaries = params.get('assets', [])

    try:
        asset_dictionaries = list(asset_dictionaries)
    except Exception:
        raise DataValidationError({'assets': 'is invalid'})

    return asset_dictionaries


def get_asset_feature_collection(params):
    asset_feature_collection = params.get('assetsGeoJson', {})

    try:
        asset_feature_collection = dict(asset_feature_collection)
    except Exception:
        raise DataValidationError({'assetsGeoJson': 'is invalid'})

    return asset_feature_collection


def get_asset_id(asset_dictionary):

    try:
        asset_id = asset_dictionary['id']
    except KeyError:
        raise DataValidationError({'id': 'is required'})

    return asset_id


def get_asset_type_code(asset_dictionary):

    try:
        asset_type_code = asset_dictionary['typeCode']
    except KeyError:
        raise DataValidationError({'typeCode': 'is required'})

    try:
        asset_type_code = AssetTypeCode(asset_type_code)
    except ValueError:
        raise DataValidationError({'typeCode': 'is invalid'})

    return asset_type_code


def get_asset_name(asset_dictionary):

    try:
        asset_name = asset_dictionary['name']
    except KeyError:
        raise DataValidationError({'name': 'is required'})

    return asset_name


def get_asset_attributes(asset_dictionary):
    value_by_key = asset_dictionary.get('attributes', {})

    try:
        value_by_key = dict(value_by_key)
    except Exception:
        raise DataValidationError({'attributes': 'is invalid'})

    return {k: v for k, v in value_by_key.items() if v not in (None, '')}


def get_asset_connections(asset_dictionary):
    asset_connections = asset_dictionary.get('connections', [])

    try:
        asset_connections = list(asset_connections)
    except Exception:
        raise DataValidationError({'connections': 'is invalid'})

    return asset_connections


def get_asset_feature_id(asset_feature):

    try:
        asset_feature_properties = asset_feature['properties']
    except KeyError:
        raise DataValidationError({'properties': 'is required'})

    try:
        asset_id = asset_feature_properties['id']
    except KeyError:
        raise DataValidationError({'id': 'is required'})

    return asset_id


def get_asset_feature_geometry(asset_feature):

    try:
        geojson_geometry = asset_feature['geometry']
    except KeyError:
        raise DataValidationError({'geometry': 'is required'})

    try:
        shapely_geometry = shape(geojson_geometry)
    except Exception:
        raise DataValidationError({'geometry': 'is invalid'})

    return shapely_geometry


def get_bus_id(connection_dictionary):

    try:
        bus_id = connection_dictionary['busId']
    except KeyError:
        raise DataValidationError({'busId': 'is required'})

    return bus_id
