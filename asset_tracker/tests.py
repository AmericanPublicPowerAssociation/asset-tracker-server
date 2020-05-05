from invisibleroads_macros_database import SpatialiteExtension
from pytest import fixture
from webtest import TestApp

from . import main as get_app


@fixture
def application(application_request):
    settings = application_request.registry.settings
    yield TestApp(get_app({}, **settings))


@fixture
def application_request(records_request, application_config):
    yield records_request


@fixture
def application_config(records_config):
    records_config.include('asset_tracker')
    yield records_config


@fixture
def database_extensions():
    return [SpatialiteExtension]
