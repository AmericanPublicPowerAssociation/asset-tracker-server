import json
import transaction
from os.path import dirname, join
from pyramid import testing
from pytest import fixture

from asset_tracker.constants import PACKAGE_FOLDER
from asset_tracker.models import (
    define_get_database_session,
    get_database_engine,
    get_transaction_manager_session)
from asset_tracker.models.meta import Base


def load_dataset_json(dataset_name):
    dataset_path = join(DATASETS_FOLDER, dataset_name)
    return json.load(open(dataset_path, 'rt'))


@fixture
def website_request(records_request):
    website_request = records_request
    yield website_request


@fixture
def records_request(posts_request, db):
    # Adapted from invisibleroads-records
    records_request = posts_request
    records_request.db = db
    yield records_request


@fixture
def posts_request(website_config):
    # Adapted from invisibleroads-posts
    posts_request = testing.DummyRequest()
    yield posts_request


@fixture
def website_config(config):
    config.include('asset_tracker')
    yield config


@fixture
def db(config):
    settings = config.get_settings()
    database_engine = get_database_engine(settings)
    Base.metadata.create_all(database_engine)
    get_database_session = define_get_database_session(database_engine)
    database_session = get_transaction_manager_session(
        get_database_session, transaction.manager)
    yield database_session
    transaction.abort()
    Base.metadata.drop_all(database_engine)


@fixture
def config(settings):
    config = testing.setUp(settings=settings)
    yield config
    testing.tearDown()


@fixture
def settings():
    return {
        'sqlalchemy.url': 'sqlite://',
    }


REPOSITORY_FOLDER = dirname(PACKAGE_FOLDER)
DATASETS_FOLDER = join(REPOSITORY_FOLDER, 'datasets')
EXAMPLE_BY_NAME = {
    'basic': {
        'assets': load_dataset_json('assets1.json'),
        'assetsGeoJson': load_dataset_json('assets1.geojson'),
    },
}
