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