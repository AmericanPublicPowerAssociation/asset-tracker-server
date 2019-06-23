import json
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPException
from pyramid.view import exception_view_config

from .constants import RECORD_ID_LENGTH
from .macros.configuration import expand_environment_variables, set_default
from .models import CLASS_REGISTRY


def main(global_config, **settings):
    settings = expand_environment_variables(settings)
    with Configurator(settings=settings) as config:
        config.include('appa_auth_client')
        config.include('asset_tracker')
        config.include('asset_vulnerability_report')
    return config.make_wsgi_app()


def includeme(config):
    settings = config.get_settings()
    config.include('pyramid_redis_sessions')
    config.include('.models')
    config.include('.routes')
    # Adapted from invisibleroads-records
    for class_name, Class in CLASS_REGISTRY.items():
        if class_name.startswith('_'):
            continue
        key = Class.__tablename__ + '.id.length'
        value = set_default(settings, key, RECORD_ID_LENGTH, int)
        setattr(Class, 'id_length', value)
    config.scan()


@exception_view_config(HTTPException)
def handle_exception(context, request):
    # Adapted from invisibleroads-posts
    status_int = context.status_int
    response = request.response
    response.status_int = status_int
    if status_int == 400:
        response.content_type = 'application/json'
        response.text = json.dumps(context.detail)
    return response
