import enum
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import LineString, Point, mapping as get_geometry_d
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import (
    Enum,
    PickleType,
    String,
    Unicode)

from .meta import Base, CreationMixin, ModificationMixin, RecordMixin
from ..constants import ASSET_TYPE_BY_ID


asset_child = Table(
    'asset_child', Base.metadata,
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
    repairing = 50
    operating = 100


class Asset(ModificationMixin, CreationMixin, RecordMixin, Base):
    __tablename__ = 'asset'
    __table_args__ = (
        UniqueConstraint(
            'utility_id', 'name', name='unique_utility_asset_name'),
    )
    utility_id = Column(String)
    name = Column(Unicode)
    status = Column(Enum(AssetStatus), default=AssetStatus.operating)
    type_id = Column(String)
    children = relationship(
        'Asset', secondary=asset_child,
        primaryjoin='asset_child.c.parent_asset_id == Asset.id',
        secondaryjoin='asset_child.c.child_asset_id == Asset.id',
        backref='parents')
    connections = relationship(
        'Asset', secondary=asset_connection,
        primaryjoin='asset_connection.c.left_asset_id == Asset.id',
        secondaryjoin='asset_connection.c.right_asset_id == Asset.id')
    attributes = Column(PickleType)
    _geometry = Column(Geometry(management=True))

    def __init__(self, **kwargs):
        if 'geometry' in kwargs:
            kwargs['_geometry'] = from_shape(kwargs.pop('geometry'))
        super(Asset, self).__init__(**kwargs)

    @property
    def primary_type(self):
        return ASSET_TYPE_BY_ID[self.primary_type_id]

    @property
    def primary_type_id(self):
        return self.type_id[0]

    @property
    def is_line(self):
        return self.primary_type_id == 'l'

    @property
    def is_locatable(self):
        return self.primary_type.get('locatable', False)

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
            if parent.is_line:
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

        if self.is_line:
            update_line_geometry(self)

    def remove_child(self, asset):
        if asset in self.children:
            self.children.remove(asset)

        if self.is_line:
            update_line_geometry(self)

    def add_connection(self, asset):
        if self == asset:
            return
        if asset not in self.connections:
            self.connections.append(asset)
        if self not in asset.connections:
            asset.connections.append(self)

    def remove_connection(self, asset):
        if asset in self.connections:
            self.connections.remove(asset)
        if self in asset.connections:
            asset.connections.remove(self)

    def get_json_d(self):
        d = dict(self.attributes or {}, **{
            'id': self.id,
            'typeId': self.type_id,
            'name': self.name,
            'parentIds': [_.id for _ in self.parents],
            'childIds': [_.id for _ in self.children],
            'connectedIds': [_.id for _ in self.connections],
        })
        if self._geometry is not None:
            d['location'] = self.location
            d['geometry'] = get_geometry_d(self.geometry)
        return d

    def is_readable(self, request):
        return True

    def is_editable(self, request):
        return True

    @classmethod
    def get_readable_ids(Class, request):
        db = request.db
        # !!! Limit to asset ids that the user has permission to view
        return [_[0] for _ in db.query(Class.id)]

    def __repr__(self):
        return f'<Asset(id={self.id})>'


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
