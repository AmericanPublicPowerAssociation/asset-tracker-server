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


class AssetStatus(enum.Enum):
    Broken = -100
    Planned = 0
    Installing = 25
    Repairing = 50
    Operational = 100


class Asset(ModificationMixin, CreationMixin, RecordMixin, Base):
    __tablename__ = 'asset'
    __table_args__ = (
        UniqueConstraint(
            'utility_id', 'name', name='unique_utility_asset_name'),
    )
    utility_id = Column(String)
    status = Column(Enum(AssetStatus), default=AssetStatus.Operational)
    shape = Column(PickleType, default={})

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
    def can_be_mass_produced(self):
        return not self.primary_type.get('unique', False)

    @property
    def is_power_source(self):
        return self.is_in_substation or self.is_in_station

    @property
    def is_in_station(self):
        return self.has_parent_type_id('S')

    @property
    def is_in_substation(self):
        return self.has_parent_type_id('s')

    def has_parent_type_id(self, primary_type_id):
        new_assets = [self]
        while new_assets:
            new_asset = new_assets.pop()
            for parent_asset in new_asset.parents:
                if parent_asset.primary_type_id == primary_type_id:
                    return True
                new_assets.append(parent_asset)
        return False

    def get_json_d(self):
        d = dict(self.attributes or {}, **{
            'id': self.id,
            'typeId': self.type_id,
            'name': self.name,
            'parentIds': [_.id for _ in self.parents],
            'childIds': [_.id for _ in self.children],
            'connectedIds': [_.id for _ in self.connections],
            'shape': self.shape != {},
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
