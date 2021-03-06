import pandas as pd

from asset_tracker.utils.errors import map_errors


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
        'typeId',
        'name'
    ])
    all_errors = map_errors(errors, lambda _: 'Missing column', {})
    if errors:
        return pd.DataFrame(), all_errors

    cols = ['utilityId', 'id', 'name']
    valid, errors = validate_field_existence_df(df, cols)
    for col in cols:
        entry = errors.get(col, None)
        if entry is not None:
            all_errors = map_errors(
                entry.id.tolist(),
                lambda _: f'{col} requires not empty value',
                all_errors)

    # !!! check valid id
    # !!! check whether user can add assets to utility id
    # !!! check valid type id

    return valid, all_errors
