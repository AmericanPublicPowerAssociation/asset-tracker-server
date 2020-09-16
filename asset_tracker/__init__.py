from invisibleroads_macros_configuration import (
    fill_environment_variables)
from pyramid.config import Configurator


def main(global_config, **settings):
    fill_environment_variables(settings)
    with Configurator(settings=settings) as config:
        includeme(config)
        config.scan()
    return config.make_wsgi_app()


def includeme(config):
    config.include('invisibleroads_records')
    config.include('.routes')
