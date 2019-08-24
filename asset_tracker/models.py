import enum
import pendulum
from datetime import datetime
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import LineString, Point, mapping
from sqlalchemy import Column, ForeignKey, Table, engine_from_config
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import configure_mappers, relationship, sessionmaker
from sqlalchemy.schema import MetaData, UniqueConstraint
from sqlalchemy.types import (
    DateTime,
    Enum,
    PickleType,
    String,
    Unicode,
    UnicodeText)
from zope.sqlalchemy import register as register_transaction_listener

from .constants import (
    ASSET_TYPE_BY_ID,
    RECORD_ID_LENGTH,
    RECORD_RETRY_COUNT)
from .exceptions import DatabaseRecordError
from .macros.security import make_random_string
from .macros.timestamp import get_timestamp


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


class AssetStatus(enum.Enum):
    broken = -100
    planned = 0
    installing = 25
    fixing = 50
    working = 100


class TaskStatus(enum.Enum):
    cancelled = -100
    new = 0
    pending = 50
    done = 100


class RecordMixin(object):
    # Adapted from invisibleroads-records

    id = Column(String, primary_key=True)
    id_length = RECORD_ID_LENGTH

    @classmethod
    def make_unique_record(Class, database, retry_count=RECORD_RETRY_COUNT):
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


class CreationMixin(object):
    # Adapted from invisibleroads-records

    creation_datetime = Column(DateTime, default=datetime.utcnow)

    @property
    def creation_timestamp(self):
        return get_timestamp(self.creation_datetime)

    @property
    def creation_when(self):
        return pendulum.instance(self.creation_datetime).diff_for_humans()

    @classmethod
    def get_datetime(Class):
        return Class.creation_datetime


class ModificationMixin(object):
    # Adapted from invisibleroads-records

    modification_datetime = Column(DateTime)

    @property
    def modification_timestamp(self):
        return get_timestamp(self.modification_datetime)

    @property
    def modification_when(self):
        return pendulum.instance(self.modification_datetime).diff_for_humans()

    @classmethod
    def get_datetime(Class):
        return Class.modification_datetime


class Asset(ModificationMixin, CreationMixin, RecordMixin, Base):

    __tablename__ = 'asset'
    utility_id = Column(String)
    name = Column(Unicode)
    status = Column(Enum(AssetStatus))
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
    _geometry = Column(Geometry(management=True))
    attributes = Column(PickleType)

    def __init__(self, **kwargs):
        if 'geometry' in kwargs:
            kwargs['_geometry'] = from_shape(kwargs.pop('geometry'))
        super(Asset, self).__init__(**kwargs)

    @property
    def is_locatable(self):
        return ASSET_TYPE_BY_ID[self.type_id[0]].get('locatable', False)

    @property
    def location(self):
        if self._geometry is None:
            return
        return self.geometry.coords[0]

    @location.setter
    def location(self, location):
        if location is None:
            self._geometry = None
            return

        point = Point(location)
        self.geometry = point

        for parent in self.parents:
            if parent.type_id == 'l':
                update_line_geometry(parent)
                continue
            if parent._geometry is not None:
                continue
            parent.geometry = point

        for child in self.children:
            if child._geometry is not None:
                continue
            child.geometry = point

    @property
    def geometry(self):
        if self._geometry is None:
            return
        return to_shape(self._geometry)

    @geometry.setter
    def geometry(self, geometry):
        if geometry is not None:
            geometry = from_shape(geometry)
        self._geometry = geometry

    def add_child(self, asset):
        if self == asset:
            return

        if asset in self.children:
            return
        self.children.append(asset)

        # If the child has no location,
        if asset.location is None:
            # Give parent location to child
            asset.location = self.location
        # If the child has a location but parent has no location,
        elif self.location is None:
            # Give location to parent
            self.location = asset.location

        if 'l' == self.type_id:
            update_line_geometry(self)

    def add_connection(self, asset):
        if self == asset:
            return
        if asset not in self.connections:
            self.connections.append(asset)
        if self not in asset.connections:
            asset.connections.append(self)

    def remove_child(self, asset):
        if asset in self.children:
            self.children.remove(asset)

        if 'l' == self.type_id:
            update_line_geometry(self)

    def remove_connection(self, asset):
        if asset in self.connections:
            self.connections.remove(asset)
        if self in asset.connections:
            asset.connections.remove(self)

    def serialize(self):
        d = dict(self.attributes or {}, **{
            'id': self.id,
            'typeId': self.type_id,
            'name': self.name,
            'connectedIds': [_.id for _ in self.connections],
            'parentIds': [_.id for _ in self.parents],
            'childIds': [_.id for _ in self.children],
        })
        if self._geometry is not None:
            d['location'] = self.location
            d['geometry'] = mapping(self.geometry)
        return d

    def __repr__(self):
        return f'<Asset(id={self.id})>'

    __table_args__ = (
        UniqueConstraint(
            'utility_id', 'name', name='unique_utility_asset_name'),
    )


class AssetTask(ModificationMixin, CreationMixin, RecordMixin, Base):
    # Record asset tasks for maintenance log
    __tablename__ = 'asset_task'
    asset_id = Column(String, ForeignKey('asset.id'))
    reference_id = Column(String)
    user_id = Column(String)
    name = Column(Unicode)
    status = Column(Enum(TaskStatus))
    description = Column(UnicodeText)


class UserEvent(CreationMixin, RecordMixin, Base):
    # Record user events for audit trail
    __tablename__ = 'user_event'
    user_id = Column(String)
    attributes = Column(PickleType)


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


def update_line_geometry(line_asset):
    line_coordinates = []
    for pole_asset in line_asset.children:
        location = pole_asset.location
        if location is None:
            continue
        line_coordinates.append(location)
    coordinate_count = len(line_coordinates)
    if coordinate_count == 0:
        geometry = None
    elif coordinate_count == 1:
        geometry = Point(line_coordinates)
    else:
        geometry = LineString(line_coordinates)
    line_asset.geometry = geometry


configure_mappers()
