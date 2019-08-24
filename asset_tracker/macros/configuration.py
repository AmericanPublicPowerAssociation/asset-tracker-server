from os.path import expandvars

from .log import get_log


L = get_log(__name__)


class Settings(dict):

    def set(self, settings, prefix, key, default=None, parse=None):
        # Adapted from invisibleroads-macros
        value = set_default(settings, prefix + key, default, parse)
        self[key] = value
        return value


def set_default(settings, key, default, parse=None):
    # Adapted from invisibleroads-macros
    value = settings.get(key, default)
    if key not in settings:
        L.warning(f'using default {key} = {value}')
    elif value in ('', None):
        L.warning(f'missing {key}')
    elif parse:
        value = parse(value)
    settings[key] = value
    return value


def parse_list(x):
    # Adapted from invisibleroads-macros
    if isinstance(x, str):
        x = x.split()
    return x


def expand_environment_variables(settings):
    return {k: expandvars(v) for k, v in settings.items()}
