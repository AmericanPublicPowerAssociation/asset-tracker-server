import enum
# from geoalchemy2 import Geometry
# from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey,
    Table, UniqueConstraint, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum, PickleType, String


Base = declarative_base()
AssetContent = Table(
    'asset_content', Base.metadata,
    Column('parent_asset_id', String, ForeignKey('asset.id')),
    Column('child_asset_id', String, ForeignKey('asset.id')))
AssetConnection = Table(
    'asset_connection', Base.metadata,
    Column('left_asset_id', String, ForeignKey('asset.id')),
    Column('right_asset_id', String, ForeignKey('asset.id')))


"""
class User(Base):
    utility_roles = [
        (utility_id, role_index),
    ]


class UserRole(enum.IntEnum):
    Spectator = 0
    Member = 1
    Leader = 2
    Administrator = 3
"""


class AssetType(enum.IntEnum):
    Station = 0
    Substation = 1
    PowerQuality = 2
    Switch = 3
    Transformer = 4
    Meter = 5
    Line = 6
    Pole = 7
    Busbar = 8
    Control = 9
    Miscellaneous = 10


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    type = Column(Enum(AssetType))
    subtype_id = Column(String, ForeignKey('asset_subtype.id'))
    utility_id = Column(String)
    properties = PickleType()
    _contents = relationship(
        'Asset', secondary=AssetContent,
        primaryjoin=AssetContent.c.parent_asset_id == id,
        secondaryjoin=AssetContent.c.child_asset_id == id,
        backref='containers')
    _connections = relationship(
        'Asset', secondary=AssetConnection,
        primaryjoin=AssetConnection.c.left_asset_id == id,
        secondaryjoin=AssetConnection.c.right_asset_id == id)
    # _geometry = Column(Geometry(management=True, use_st_prefix=False))
    # _geometry = Column(Geometry(srid=4326))

    def __init__(self, **kwargs):
        if 'geometry' in kwargs:
            geometry = kwargs.pop('geometry')
            kwargs['_geometry'] = geometry.wkt
        super(Asset, self).__init__(**kwargs)

    def __repr__(self):
        return '<Asset(id={})>'.format(self.id)

    @property
    def contained_assets(self):
        return self._contents

    @property
    def connected_assets(self):
        return self._connections

    @property
    def geometry(self):
        return Point(self.longitude, self.latitude)

    def add_content(self, asset):
        if self == asset:
            return
        if asset not in self._contents:
            self._contents.append(asset)

    def add_connection(self, asset):
        if self == asset:
            return
        if asset not in self._connections:
            self._connections.append(asset)
        if self not in asset._connections:
            asset._connections.append(self)

    def remove_content(self, asset):
        if asset in self._contents:
            self._contents.remove(asset)

    def remove_connection(self, asset):
        if asset in self._connections:
            self._connections.remove(asset)
        if self in asset._connections:
            asset._connections.remove(self)


class AssetSubType(Base):
    __tablename__ = 'asset_subtype'
    id = Column(String, primary_key=True)
    name = Column(String)
    type_id = Column(Enum(AssetType))


class VulnerableAsset(Base):
    __tablename__ = 'vulnerable_asset'
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey('asset.id'), nullable=False)
    vulnerability_description = Column(String, nullable=False)
    vulnerability_date_published = Column(DateTime, nullable=False)
    vulnerability_score = Column(Float)
    UniqueConstraint('asset_id', 'id')


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


engine = create_engine('sqlite:///app.db')
load_spatialite_sqlite_extension(engine)
Base.metadata.create_all(engine)
