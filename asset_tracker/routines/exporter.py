# TODO: Consider renaming
import pandas as pd


def build_flat_dict_structure(asset):
    asset_json = asset.get_json_dictionary()
    attributes = asset.attributes.copy()
    del asset_json['attributes']

    flat_asset = {
        **asset_json,
        **attributes,
        'wkt': asset.geometry.wkt if asset.geometry else '',
    }

    return flat_asset


def validate_field_existence_df(df, fields):
    invalid_rows = {}
    invalid_ids = set()

    for field in fields:
        invalid_rows[field] = df[df[field].isnull()]
        invalid_ids.update(invalid_rows[field]['id'])

    valid_df = df[~df.id.isin(invalid_ids)]

    return valid_df, invalid_rows


def validate_row_existence_df(df, fields):
    columns = df.columns.tolist()
    return [field for field in fields if field not in columns]


def validate_assets_df(assets_data_frame):
    errors = []

    df = assets_data_frame.dropna(how='all')
    df.replace(r'^\s*$', pd.np.nan, regex=True, inplace=True)

    errors = validate_row_existence_df(df, [
        'id',
        'typeCode',
        'name'
    ])
    all_errors = map_errors(errors, lambda _: 'Missing column', {})
    if errors:
        return pd.DataFrame(), all_errors

    cols = ['typeCode', 'id', 'name']
    valid, errors = validate_field_existence_df(df, cols)
    for col in cols:
        entry = errors.get(col, None)
        if entry is not None:
            all_errors = map_errors(
                entry.id.tolist(),
                lambda _: f'{col} requires not empty value',
                all_errors)

    return valid, all_errors


def map_errors(keys, mapf, errors):
    _errors = errors.copy()
    for key in keys:
        _errors[key] = _errors.get(key, [])
        _errors[key].append(mapf(key))

    return _errors


def get_extra_columns_df(df, fields):
    columns = df.columns.tolist()
    return [field for field in columns if field not in fields]
