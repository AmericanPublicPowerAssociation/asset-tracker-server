from pyramid.config import Configurator


def main(global_config, **settings):
    with Configurator(settings=settings) as config:
        includeme(config)
        config.scan()
    return config.make_wsgi_app()


def includeme(config):
    config.include('invisibleroads_posts')
    config.include('invisibleroads_records')
    config.include('.routes')
