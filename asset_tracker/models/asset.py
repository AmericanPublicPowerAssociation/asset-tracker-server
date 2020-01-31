from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    PickleType,
    String)

from .meta import Base


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String, primary_key=True)
    name = Column(String)
    type_code = Column(String)
    attributes = Column(PickleType)
    connections = relationship('Connection')

    def __repr__(self):
        return f'<Asset({self.id})>'


class Bus(Base):
    __tablename__ = 'bus'
    id = Column(String, primary_key=True)

    def __repr__(self):
        return f'<Bus({self.id})>'


class Connection(Base):
    __tablename__ = 'connection'
    asset_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    bus_id = Column(String, ForeignKey('bus.id'), primary_key=True)
    attributes = Column(PickleType)

    def __repr__(self):
        argument_string = ', '.join((
            f'asset_id={self.asset_id}',
            f'bus_id={self.bus_id}',
        ))
        return f'<Connection({argument_string})>'


class LineType(Base):
    __tablename__ = 'line_type'
    id = Column(String, primary_key=True)
    attributes = Column(PickleType)
