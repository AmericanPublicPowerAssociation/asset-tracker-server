from pyramid.config import Configurator
from sqlalchemy import engine_from_config
# from .models import DBSession, Base


def main(global_config, **settings):
    print(settings)
    config = Configurator(settings=settings)
    config.add_route('hello', '/hello')
    config.add_route('home', '/')
    config.add_route('asset', '/asset')
    config.add_route('assets', '/assets')
    config.add_route('task', '/task')
    config.add_route('tasks', '/tasks')
    config.include('.models')
    config.scan('.views')
    config.scan('.asset')
    config.scan('.task')
    return config.make_wsgi_app()
