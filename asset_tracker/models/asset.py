import enum
from invisibleroads_records.models import (
    Base,
    CreationMixin,
    ModificationMixin,
    RecordMixin)
from shapely.geometry import mapping as get_geojson_dictionary
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Enum,
    Integer,
    String,
    Unicode)

from .meta import (
    AttributesMixin,
    DeletionMixin,
    GeometryMixin)


class AssetTypeCode(enum.Enum):
    LINE = 'l'
    METER = 'm'
    TRANSFORMER = 't'
    GENERATOR = 'g'
    SUBSTATION = 's'
    SWITCH = 'x'
    STATION = 'S'
    STORAGE = 'o'
    POWERQUALITY = 'q'
    CAPACITOR = 'qc'
    REGULATOR = 'rr'
    CONTROL = 'c'


class Asset(
        AttributesMixin,
        GeometryMixin,
        DeletionMixin,
        ModificationMixin,
        CreationMixin,
        RecordMixin,
        Base):
    __tablename__ = 'asset'
    type_code = Column(Enum(AssetTypeCode))
    name = Column(Unicode)
    connections = relationship('Connection', cascade='all, delete-orphan')

    def get_json_dictionary(self):
        d = self.get_json_dictionary_without_id()
        d['id'] = self.id
        return d

    def get_json_dictionary_without_id(self):
        return {
            'typeCode': self.type_code.value,
            'name': self.name,
            'attributes': self.attributes,
            'connections': {_.asset_vertex_index: {
                'busId': _.bus_id,
                'attributes': _.attributes,
            } for _ in self.connections},
        }

    def get_geojson_feature(self):
        return {
            'type': 'Feature',
            'properties': {
                'id': self.id,
                # !!! Remove if view splits assets by type
                'typeCode': self.type_code.value,
            },
            'geometry': get_geojson_dictionary(self.geometry),
        }

    @classmethod
    def get_viewable_ids(Class, request):
        db = request.db
        return [_[0] for _ in db.query(Asset.id).filter_by(is_deleted=False)]

    def __repr__(self):
        return f'<Asset({self.id})>'


class Bus(RecordMixin, Base):
    __tablename__ = 'bus'

    def __repr__(self):
        return f'<Bus({self.id})>'


class Connection(AttributesMixin, Base):
    __tablename__ = 'connection'
    # asset_id = Column(String, ForeignKey('asset.id'), primary_key=True, ondelete='CASCADE')
    asset_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    asset_vertex_index = Column(Integer)
    # bus_id = Column(String, ForeignKey('bus.id'), primary_key=True, ondelete='CASCADE')
    bus_id = Column(String, ForeignKey('bus.id'), primary_key=True)

    def __repr__(self):
        argument_string = ', '.join((
            f'asset_id={self.asset_id}',
            f'asset_vertex_index={self.asset_vertex_index}',
            f'bus_id={self.bus_id}',
        ))
        return f'<Connection({argument_string})>'


class LineType(AttributesMixin, Base):
    __tablename__ = 'line_type'
    id = Column(String, primary_key=True)
