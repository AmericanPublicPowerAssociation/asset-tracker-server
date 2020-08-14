from shapely.geometry import shape

from ..constants.asset import ASSET_TYPE_BY_CODE
from ..exceptions import DataValidationError
from ..macros.database import RecordIdMirror
from ..models import Asset, AssetTypeCode, Bus, Connection


def absorb_asset_type_by_code(delta_asset_type_by_code):
    for type_code, delta_asset_type in delta_asset_type_by_code.items():
        asset_type = ASSET_TYPE_BY_CODE[type_code]
        for key in [
            'assetAttributes',
            'connectionAttributes',
        ]:
            delta_values = delta_asset_type.get(key, [])
            if not delta_values:
                continue
            asset_type[key] = asset_type.get(key, []) + delta_values


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


def get_asset_dictionary_by_id(params):
    asset_dictionary_by_id = params.get('assetById', {})

    try:
        asset_dictionary_by_id = dict(asset_dictionary_by_id)
    except Exception:
        raise DataValidationError({'assetById': 'is invalid'})

    for asset_id, asset_dictionary in asset_dictionary_by_id.items():
        try:
            asset_dictionary_by_id[asset_id] = dict(asset_dictionary)
        except Exception:
            raise DataValidationError({'assetById': 'has invalid values'})

    return asset_dictionary_by_id


def get_asset_feature_collection(params):
    asset_feature_collection = params.get('assetsGeoJson', {})

    try:
        asset_feature_collection = dict(asset_feature_collection)
    except Exception:
        raise DataValidationError({'assetsGeoJson': 'is invalid'})

    try:
        asset_features = list(asset_feature_collection.get('features', []))
    except Exception:
        raise DataValidationError({'assetsGeoJson': 'has invalid values'})

    asset_feature_collection['features'] = asset_features
    return asset_feature_collection


def update_assets(
    db,
    asset_dictionary_by_id,
    asset_id_mirror,
    editable_utility_ids,
):
    error_by_id = {}

    for asset_id, asset_dictionary in asset_dictionary_by_id.items():
        try:
            asset_utility_id = get_asset_utility_id(asset_dictionary)
            asset_type_code = get_asset_type_code(asset_dictionary)
            asset_name = get_asset_name(asset_dictionary)
            asset_attributes = get_asset_attributes(asset_dictionary)
            asset_is_deleted = get_asset_is_deleted(asset_dictionary)
        except DataValidationError as e:
            error_by_id[asset_id] = e.args[0]
            continue

        asset_id = asset_id_mirror.get(asset_id)
        asset = db.query(Asset).get(asset_id)

        if not asset:
            asset = Asset.make_unique_record(db)
            asset_id = asset_id_mirror.set(asset_id, asset.id)
        elif asset.utility_id not in editable_utility_ids:
            # Skip if we do not have edit permission
            error_by_id[asset_id] = {'assetById': 'has uneditable assets'}
            continue

        asset.utility_id = asset_utility_id
        asset.type_code = asset_type_code
        asset.name = asset_name
        asset.attributes = asset_attributes
        asset.is_deleted = asset_is_deleted
        db.add(asset)

    if error_by_id:
        raise DataValidationError(error_by_id)


def update_asset_connections(
    db,
    asset_dictionary_by_id,
    asset_id_mirror,
    editable_utility_ids,
):
    error_by_id = {}
    bus_id_mirror = RecordIdMirror()
    for asset_id, asset_dictionary in asset_dictionary_by_id.items():
        try:
            connection_by_index = get_asset_connections(asset_dictionary)
        except DataValidationError as e:
            error_by_id[asset_id] = e.args[0]
            continue
        asset_id = asset_id_mirror.get(asset_id)
        asset = db.query(Asset).get(asset_id)
        if not asset:
            error_by_id[asset_id] = {'assetById': 'has invalid keys'}
            continue
        elif asset.utility_id not in editable_utility_ids:
            error_by_id[asset_id] = {'assetById': 'has uneditable assets'}
            continue
        connections = []
        for (
            asset_vertex_index,
            connection_dictionary,
        ) in connection_by_index.items():
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
            connection.attributes = connection_dictionary.get('attributes', {})
            connection.asset_vertex_index = asset_vertex_index
            connections.append(connection)
        asset.connections = connections
    if error_by_id:
        raise DataValidationError(error_by_id)


def update_asset_geometries(
    db,
    asset_feature_collection,
    asset_id_mirror,
    editable_utility_ids,
):
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
        if not asset:
            error_by_index[index] = {'assetsGeoJson': 'has invalid properties'}
            continue
        elif asset.utility_id not in editable_utility_ids:
            error_by_index[index] = {'assetsGeoJson': 'has uneditable assets'}
            continue
        if asset.geometry != asset_geometry:
            asset.geometry = asset_geometry
        db.add(asset)

    if error_by_index:
        raise DataValidationError(error_by_index)


def get_asset_utility_id(asset_dictionary):
    try:
        asset_utility_id = asset_dictionary['utilityId']
    except KeyError:
        raise DataValidationError({'utilityId': 'is required'})
    return asset_utility_id


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
    attribute_value_by_name = asset_dictionary.get('attributes', {})

    try:
        attribute_value_by_name = dict(attribute_value_by_name)
    except Exception:
        raise DataValidationError({'attributes': 'is invalid'})

    return {
        name: value for name, value in attribute_value_by_name.items()
        if value not in (None, '')}


def get_asset_is_deleted(asset_dictionary):
    is_deleted = asset_dictionary.get('isDeleted', False)
    try:
        is_deleted = bool(is_deleted)
    except Exception:
        raise DataValidationError({'isDeleted': 'is invalid'})
    return is_deleted


def get_asset_connections(asset_dictionary):
    raw_connection_by_index = asset_dictionary.get('connections', {})
    try:
        raw_connection_by_index = dict(raw_connection_by_index)
    except Exception:
        raise DataValidationError({'connections': 'is invalid'})

    connection_by_index = {}
    for index, connection in raw_connection_by_index.items():
        try:
            index = int(index)
        except Exception:
            raise DataValidationError({
                'connections': 'has invalid indices'})

        try:
            connection = dict(connection)
        except Exception:
            raise DataValidationError({
                'connections': 'has invalid values'})

        attributes = connection.get('attributes', {})
        try:
            connection['attributes'] = dict(attributes)
        except Exception:
            raise DataValidationError({
                'connections': 'has invalid attributes'})

        connection_by_index[index] = connection

    return connection_by_index


def get_bus_id(connection_dictionary):

    try:
        bus_id = connection_dictionary['busId']
    except KeyError:
        raise DataValidationError({'busId': 'is required'})

    return bus_id


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
