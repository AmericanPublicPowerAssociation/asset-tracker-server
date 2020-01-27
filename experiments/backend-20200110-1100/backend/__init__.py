from pyramid.config import Configurator
from sqlalchemy import engine_from_config
# from .models import DBSession, Base


def main(global_config, **settings):
    print(settings)
    config = Configurator(settings=settings)
    config.include('.models')
    config.include('.routes')
    config.scan('.views')
    return config.make_wsgi_app()
