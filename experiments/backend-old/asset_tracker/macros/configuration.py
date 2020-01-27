class Settings(dict):

    def set(self, settings, prefix, key, default=None, parse=None):
        # Adapted from invisibleroads-macros
        value = set_default(settings, prefix + key, default, parse)
        self[key] = value
        return value


def parse_list(x):
    # Adapted from invisibleroads-macros
    if isinstance(x, str):
        x = x.split()
    return x
