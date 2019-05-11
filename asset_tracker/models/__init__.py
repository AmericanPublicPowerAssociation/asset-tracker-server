import zope.sqlalchemy
from sqlalchemy import engine_from_config
from sqlalchemy.orm import configure_mappers, sessionmaker

from .asset import Asset  # noqa


configure_mappers()


def get_database_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_database_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    database_session = session_factory()
    zope.sqlalchemy.register(
        database_session, transaction_manager=transaction_manager)
    return database_session


def includeme(config):
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'
    config.include('pyramid_tm')
    config.include('pyramid_retry')
    database_engine = get_database_engine(settings)
    database_session_factory = get_database_session_factory(database_engine)
    config.add_request_method(
        lambda r: get_tm_session(database_session_factory, r.tm),
        'db', reify=True)
