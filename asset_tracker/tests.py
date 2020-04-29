from pytest import fixture
from webtest import TestApp

from . import main as get_app


@fixture
def application(application_request):
    settings = application_request.registry.settings
    yield TestApp(get_app({}, **settings))


@fixture
def application_request(records_request):
    yield records_request
