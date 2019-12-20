from sqlalchemy import Column, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import PickleType, String


engine = create_engine('sqlite:///local.sqlite', echo=True)
Base = declarative_base()


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String, primary_key=True)
    name = Column(String)
    type_code = Column(String)
    attributes = Column(PickleType)

    def __repr__(self):
        return f'<Asset({self.id})>'


class ElectricalConnection(Base):
    __tablename__ = 'electrical_connection'
    asset_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    bus_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    attributes = Column(PickleType)

    def __repr__(self):
        argument_string = ', '.join((
            f'asset_id={self.asset_id}',
            f'bus_id={self.bus_id}',
        ))
        return f'<ElectricalConnection({argument_string})>'


class LineType(Base):
    __tablename__ = 'line_type'
    id = Column(String, primary_key=True)
    attributes = Column(PickleType)


if __name__ == '__main__':
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
db = Session()
