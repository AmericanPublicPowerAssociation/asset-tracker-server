from sqlalchemy import engine_from_config
from sqlalchemy.orm import configure_mappers, sessionmaker
from zope.sqlalchemy import register as register_transaction_listener

from .asset import Asset, AssetTypeCode, Bus, Connection  # noqa
# from .asset import Asset, AssetStatus         # noqa
# from .log import Log, LogEvent                # noqa
# from .task import Task, TaskNote, TaskStatus  # noqa


def includeme(config):
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    config.include('pyramid_tm')
    config.include('pyramid_retry')
    database_engine = get_database_engine(settings)
    get_database_session = define_get_database_session(database_engine)
    config.add_request_method(
        lambda r: get_transaction_manager_session(get_database_session, r.tm),
        'db', reify=True)


def get_database_engine(settings, prefix='sqlalchemy.'):
    engine = engine_from_config(settings, prefix)
    if settings[prefix + 'url'].startswith('sqlite'):
        load_spatialite_sqlite_extension(engine)
    return engine


def define_get_database_session(database_engine):
    get_database_session = sessionmaker()
    get_database_session.configure(bind=database_engine)
    return get_database_session


def get_transaction_manager_session(get_database_session, transaction_manager):
    database_session = get_database_session()
    register_transaction_listener(
        database_session, transaction_manager=transaction_manager)
    return database_session


def load_spatialite_sqlite_extension(engine):
    from sqlalchemy.event import listen
    from sqlalchemy.sql import func, select

    def load_spatialite(api_connection, connection_record):
        api_connection.enable_load_extension(True)
        api_connection.load_extension('mod_spatialite.so')

    listen(engine, 'connect', load_spatialite)
    engine_connection = engine.connect()
    engine_connection.execute(select([func.InitSpatialMetaData()]))
    engine_connection.close()
    return engine


configure_mappers()
