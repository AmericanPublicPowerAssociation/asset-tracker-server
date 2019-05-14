from sqlalchemy import Column, Index, engine_from_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers, sessionmaker
from sqlalchemy.schema import MetaData
from sqlalchemy.types import PickleType, String
from zope.sqlalchemy import register as register_transaction_listener

from .constants import RECORD_ID_LENGTH, RECORD_RETRY_COUNT
from .exceptions import DatabaseRecordError
from .macros.security import make_random_string


CLASS_REGISTRY = {}
metaData = MetaData(naming_convention={
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
})
Base = declarative_base(class_registry=CLASS_REGISTRY, metadata=metaData)


class RecordMixin(object):

    id = Column(String, primary_key=True)
    id_length = RECORD_ID_LENGTH

    @classmethod
    def make_unique_record(Class, database, retry_count=RECORD_RETRY_COUNT):
        # Adapted from invisibleroads-records
        count = 0
        id_length = Class.id_length
        while count < retry_count:
            record = Class(id=make_random_string(id_length))
            database.add(record)
            try:
                database.flush()
            except IntegrityError:
                database.rollback()
            else:
                break
            count += 1
        else:
            raise DatabaseRecordError(
                f'could not make unique {Class.__tablename__}')
        return record


class Asset(RecordMixin, Base):
    __tablename__ = 'asset'
    utility_id = Column(String)
    name = Column(String)
    type_id = Column(String)
    attributes = PickleType()

    def __repr__(self):
        return f'<Asset(id={self.id})>'


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
    return engine_from_config(settings, prefix)


def define_get_database_session(database_engine):
    get_database_session = sessionmaker()
    get_database_session.configure(bind=database_engine)
    return get_database_session


def get_transaction_manager_session(get_database_session, transaction_manager):
    database_session = get_database_session()
    register_transaction_listener(
        database_session, transaction_manager=transaction_manager)
    return database_session


Index('utility_asset_name', Asset.utility_id, Asset.name, unique=True)


configure_mappers()
