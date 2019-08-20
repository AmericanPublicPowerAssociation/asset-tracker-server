from collections import Iterable


def split(value, cast=None):
    if isinstance(value, str):
        elements = value.split(',')
        print(cast)
        if cast:
            elements = [cast(element) for element in elements]

        return elements
    return []


def restore_array_to_csv(df, column, cast=None):
    df[column] = df[column].apply(split, cast=cast)
    return df


def cast_coordinate_or_list(data, separator, cast=float):
    data_split = data.split(separator)
    if len(data_split) >= 2:
        return [cast(element) for element in data_split]

    return cast(data)


def get_extra_columns_df(df, fields):
    columns = df.columns.tolist()
    return [field for field in columns if field not in fields]


def join_items(items, sep):
    return f'{sep}'.join([str(item) for item in items])


def list_to_csv(data):
    if isinstance(data, list):
        values = []
        for entry in data:
            if isinstance(entry, Iterable) and type(entry) != str:
                values.append(join_items(entry, sep='\t'))
            else:
                values.append(str(entry))

        return join_items(values, ',')

    return ''


def transform_array_to_csv(df, column):
    df[column] = df[column].apply(list_to_csv)
    return df


def build_flat_dict_structure(asset):
    flat_asset = {
        'id': asset.id,
        'utilityId': asset.utility_id,
        'typeId': asset.type_id,
        'name': asset.name,
        'location': asset.location,
        'parentIds': [asset.id for asset in asset.parents],
        'childIds': [asset.id for asset in asset.children],
        'connectedIds': [asset.id for asset in asset.connections]
    }

    if asset.geometry:
        flat_asset['geometry_type'] = asset.geometry.type
        if asset.geometry.type == 'Point':
            flat_asset['geometry_coordinates'] = asset.geometry.coords[0]
        else:
            flat_asset['geometry_coordinates'] = list(asset.geometry.coords)

    if asset.attributes:
        flat_asset.update(asset.attributes)

    return flat_asset