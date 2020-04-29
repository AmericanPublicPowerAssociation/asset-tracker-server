import transaction
from pyramid import testing
from pytest import fixture

from asset_tracker.models import (
    define_get_database_session,
    get_database_engine,
    get_transaction_manager_session)
from asset_tracker.models.meta import Base


@fixture
def website_request(records_request):
    website_request = records_request
    yield website_request


@fixture
def application_config(config):
    config.include('asset_tracker')
    yield config
