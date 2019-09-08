from sqlalchemy import Column
from sqlalchemy.types import (
    PickleType,
    String)

from .meta import Base, CreationMixin, RecordMixin


class UserEvent(CreationMixin, RecordMixin, Base):
    __tablename__ = 'user_event'
    user_id = Column(String)
    attributes = Column(PickleType)
