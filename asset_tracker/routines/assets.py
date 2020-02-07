from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from ..exceptions import DataValidationError
from ..models import Asset, AssetTypeCode, Bus, Connection


def update_assets(db, asset_dictionaries, asset_id_by_temporary_id):
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

        asset_id = asset_id_by_temporary_id.get(asset_id, asset_id)
        asset = db.query(Asset).get(asset_id)
        if not asset:
            asset = Asset.make_unique_record(db)
            asset_id_by_temporary_id[asset_id] = asset.id
            asset_id = asset.id

        asset.type_code = asset_type_code
        asset.name = asset_name
        asset.attributes = asset_attributes
        db.add(asset)

    if error_by_index:
        raise DataValidationError(error_by_index)


def update_asset_connections(db, asset_dictionaries, asset_id_by_temporary_id):
    error_by_index = {}
    bus_id_by_temporary_id = {}

    for index, asset_dictionary in enumerate(asset_dictionaries):
        try:
            asset_id = get_asset_id(asset_dictionary)
            connection_dictionaries = get_asset_connections(asset_dictionary)
        except DataValidationError as e:
            error_by_index[index] = e.args[0]
            continue

        asset_id = asset_id_by_temporary_id.get(asset_id, asset_id)
        asset = db.query(Asset).get(asset_id)

        connections = []
        for connection_dictionary in connection_dictionaries:
            bus_id = get_bus_id(connection_dictionary)
            bus_id = bus_id_by_temporary_id.get(bus_id, bus_id)
            bus = db.query(Bus).get(bus_id)
            if not bus:
                bus = Bus.make_unique_record(db)
                bus_id_by_temporary_id[bus_id] = bus.id
                bus_id = bus.id
            db.add(bus)
            connection = db.query(Connection).get({
                'asset_id': asset_id, 'bus_id': bus_id})
            if not connection:
                connection = Connection(bus_id=bus_id)
                connection.attributes = connection_dictionary.get(
                    'attributes', {})
            connections.append(connection)
        asset.connections = asset

    if error_by_index:
        raise DataValidationError(error_by_index)


def update_asset_geometries(
        db, asset_feature_collection, asset_id_by_temporary_id):
    error_by_index = {}
    asset_features = asset_feature_collection['features']

    for index, asset_feature in enumerate(asset_features):
        try:
            asset_id = get_asset_feature_id(asset_feature)
            asset_geometry = get_asset_feature_geometry(asset_feature)
        except DataValidationError as e:
            error_by_index[index] = e.args[0]
            continue

        asset_id = asset_id_by_temporary_id.get(asset_id, asset_id)
        asset = db.query(Asset).get(asset_id)
        asset.geometry = from_shape(asset_geometry)
        db.add(asset)

    if error_by_index:
        raise DataValidationError(error_by_index)


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
    asset_attributes = asset_dictionary.get('attributes', {})

    try:
        asset_attributes = dict(asset_attributes)
    except Exception:
        raise DataValidationError({'attributes': 'is invalid'})

    return asset_attributes


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
