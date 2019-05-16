import json
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest

from .constants import RECORD_ID_LENGTH
from .macros.configuration import set_default
from .models import CLASS_REGISTRY


def main(global_config, **settings):
    with Configurator(settings=settings) as config:
        config.include('asset_tracker')
    return config.make_wsgi_app()


def includeme(config):
    settings = config.get_settings()
    config.include('.models')
    config.include('.routes')
    # Adapted from invisibleroads-records
    for class_name, Class in CLASS_REGISTRY.items():
        if class_name.startswith('_'):
            continue
        key = Class.__tablename__ + '.id.length'
        value = set_default(settings, key, RECORD_ID_LENGTH, int)
        setattr(Class, 'id_length', value)
    config.add_view(handle_bad_request, context=HTTPBadRequest)
    config.scan()


def handle_bad_request(context, request):
    # Adapted from invisibleroads-posts
    response = request.response
    response.status_int = context.status_int
    response.content_type = 'application/json'
    response.text = json.dumps(context.detail)
    return response
