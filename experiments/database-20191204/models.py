from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Integer,
    PickleType,
    String)


Base = declarative_base()


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String, primary_key=True)
    type_id = Column(String)
    electrical_connections = relationship(
        'ElectricalConnection', back_populates='asset')
    attributes = Column(PickleType)

    def __repr__(self):
        return f'<Asset({self.id})>'


class Busbar(Base):
    __tablename__ = 'busbar'
    id = Column(String, primary_key=True)
    electrical_connections = relationship(
        'ElectricalConnection', back_populates='busbar')

    def __repr__(self):
        return f'<Busbar({self.id})>'


class ElectricalConnection(Base):
    __tablename__ = 'electrical_connection'
    asset_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    asset = relationship('Asset', back_populates='electrical_connections')
    busbar_id = Column(String, ForeignKey('busbar.id'), primary_key=True)
    busbar = relationship('Busbar', back_populates='electrical_connections')
    busbar_node = Column(Integer)

    def __repr__(self):
        keyword_strings = [
            f'asset_id={self.asset_id}',
            f'busbar_id={self.busbar_id}',
            f'busbar_node={self.busbar_node}',
        ]
        argument_string = ', '.join(keyword_strings)
        return f'<ElectricalConnection({argument_string})>'
