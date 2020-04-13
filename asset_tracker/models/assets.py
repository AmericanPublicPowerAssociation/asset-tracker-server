import enum
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Enum,
    String,
    Unicode)
from shapely.geometry import mapping as get_geojson_dictionary

from .meta import (
    AttributesMixin,
    Base,
    CreationMixin,
    DeletionMixin,
    GeometryMixin,
    ModificationMixin,
    RecordMixin)


class AssetTypeCode(enum.Enum):
    LINE = 'l'
    METER = 'm'
    TRANSFORMER = 't'
    SUBSTATION = 's'


class Asset(
        GeometryMixin,
        AttributesMixin,
        ModificationMixin,
        CreationMixin,
        DeletionMixin,
        RecordMixin,
        Base):
    __tablename__ = 'asset'
    type_code = Column(Enum(AssetTypeCode))
    name = Column(Unicode)
    connections = relationship('Connection', cascade='all, delete-orphan')

    def get_json_dictionary(self):
        return {
            'id': self.id,
            'typeCode': self.type_code.value,
            'name': self.name,
            'attributes': self.attributes,
            'connections': [{
                'busId': _.bus_id,
                'attributes': _.attributes,
            } for _ in self.connections],
        }

    def get_geojson_feature(self):
        properties = {'id': self.id, 'typeCode': self.type_code.value}
        return {
            'type': 'Feature',
            'properties': properties,
            'geometry': get_geojson_dictionary(self.geometry),
        }

    @classmethod
    def get_viewable_ids(Class, request):
        db = request.db
        assets = db.query(Asset.id).filter_by(is_deleted=False)
        return [_[0] for _ in assets]

    def __repr__(self):
        return f'<Asset({self.id})>'


class Bus(RecordMixin, Base):
    __tablename__ = 'bus'

    def __repr__(self):
        return f'<Bus({self.id})>'


class Connection(AttributesMixin, Base):
    __tablename__ = 'connection'
    asset_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    bus_id = Column(String, ForeignKey('bus.id'), primary_key=True)

    def __repr__(self):
        argument_string = ', '.join((
            f'asset_id={self.asset_id}',
            f'bus_id={self.bus_id}',
        ))
        return f'<Connection({argument_string})>'


class LineType(AttributesMixin, Base):
    __tablename__ = 'line_type'
    id = Column(String, primary_key=True)
