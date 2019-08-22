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