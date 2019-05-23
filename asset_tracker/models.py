from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy import Column, ForeignKey, Table, engine_from_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers, relationship, sessionmaker
from sqlalchemy.schema import MetaData, UniqueConstraint
from sqlalchemy.types import PickleType, String
from zope.sqlalchemy import register as register_transaction_listener

from .constants import RECORD_ID_LENGTH, RECORD_RETRY_COUNT
from .exceptions import DatabaseRecordError
from .macros.security import make_random_string


CLASS_REGISTRY = {}
metadata = MetaData(naming_convention={
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
})
Base = declarative_base(class_registry=CLASS_REGISTRY, metadata=metadata)
asset_content = Table(
    'asset_content', Base.metadata,
    Column('parent_asset_id', String, ForeignKey('asset.id')),
    Column('child_asset_id', String, ForeignKey('asset.id')))
asset_connection = Table(
    'asset_connection', Base.metadata,
    Column('left_asset_id', String, ForeignKey('asset.id')),
    Column('right_asset_id', String, ForeignKey('asset.id')))


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
    children = relationship(
        'Asset', secondary=asset_content,
        primaryjoin='asset_content.c.parent_asset_id == Asset.id',
        secondaryjoin='asset_content.c.child_asset_id == Asset.id',
        backref='parents')
    connections = relationship(
        'Asset', secondary=asset_connection,
        primaryjoin='asset_connection.c.left_asset_id == Asset.id',
        secondaryjoin='asset_connection.c.right_asset_id == Asset.id')
    _geometry = Column(Geometry(management=True, use_st_prefix=False))
    attributes = PickleType()

    def __init__(self, **kwargs):
        if 'geometry' in kwargs:
            kwargs['_geometry'] = from_shape(kwargs.pop('geometry'))
        super(Asset, self).__init__(**kwargs)

    @property
    def geometry(self):
        return to_shape(self._geometry)

    @geometry.setter
    def geometry(self, g):
        self._geometry = from_shape(g)

    def add_child(self, asset):
        if self == asset:
            return
        if asset not in self.children:
            self.children.append(asset)

    def add_connection(self, asset):
        if self == asset:
            return
        if asset not in self.connections:
            self.connections.append(asset)
        if self not in asset.connections:
            self.connections.append(self)

    def remove_child(self, asset):
        if asset in self.children:
            self.children.remove(asset)

    def remove_connection(self, asset):
        if asset in self.connections:
            self.connections.remove(asset)
        if self in asset.connections:
            asset.connections.remove(self)

    def serialize(self):
        return {
            'id': self.id,
            'typeId': self.type_id,
            'name': self.name,
        }

    def __repr__(self):
        return f'<Asset(id={self.id})>'

    __table_args__ = (
        UniqueConstraint(
            'utility_id', 'name', name='unique_utility_asset_name'),
    )


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
        api_connection.load_extension('/usr/lib64/mod_spatialite.so')

    listen(engine, 'connect', load_spatialite)
    engine_connection = engine.connect()
    engine_connection.execute(select([func.InitSpatialMetaData()]))
    engine_connection.close()
    return engine


configure_mappers()
