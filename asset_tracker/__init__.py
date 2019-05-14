from pyramid.config import Configurator

from .constants import RECORD_ID_LENGTH
from .macros.configuration import set_default
from .models import CLASS_REGISTRY


def main(global_config, **settings):
    with Configurator(settings=settings) as config:
        config.include('.models')
        config.include('.routes')
        config.scan()
    # Adapted from invisibleroads-macros
    for class_name, Class in CLASS_REGISTRY.items():
        if class_name.startswith('_'):
            continue
        key = Class.__tablename__ + '.id.length'
        value = set_default(settings, key, RECORD_ID_LENGTH, int)
        setattr(Class, 'id_length', value)
    return config.make_wsgi_app()
