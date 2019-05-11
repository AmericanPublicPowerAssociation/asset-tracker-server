from sqlalchemy import Column, Index
from sqlalchemy.types import PickleType, String
from .meta import Base


class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String, primary_key=True)
    utility_id = Column(String)
    name = Column(String)
    type_id = Column(String)
    attributes = PickleType()

    def __repr__(self):
        return f'<Asset(id={self.id})>'


Index('utility_asset_name', Asset.utility_id, Asset.name, unique=True)
