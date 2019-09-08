from sqlalchemy import Column
from sqlalchemy.types import (
    PickleType,
    String)

from .meta import Base, CreationMixin, RecordMixin


class Log(CreationMixin, RecordMixin, Base):
    __tablename__ = 'log'
    user_id = Column(String)
    attributes = Column(PickleType)
