def map_errors(keys, mapf, errors):
    _errors = errors.copy()
    for key in keys:
        _errors[key] = _errors.get(key, [])
        _errors[key].append(mapf(key))

    return _errors