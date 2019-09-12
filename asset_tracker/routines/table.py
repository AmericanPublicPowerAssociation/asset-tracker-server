def prepare_column(t, column_name, cast, separator=','):
    t[column_name] = t[column_name].apply(
        split, cast=cast, separator=separator)


def split(x, cast=None, separator=','):
    if not isinstance(x, str):
        return []
    elements = x.split(separator)
    if cast:
        elements = [cast(_) for _ in elements]
    return elements
