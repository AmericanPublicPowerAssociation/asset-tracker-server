import enum
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import (
    Enum,
    String,
    Unicode,
    UnicodeText)

from .meta import Base, CreationMixin, ModificationMixin, RecordMixin


class TaskStatus(enum.Enum):
    cancelled = -100
    new = 0
    pending = 50
    done = 100


class Task(ModificationMixin, CreationMixin, RecordMixin, Base):
    __tablename__ = 'task'
    asset_id = Column(String, ForeignKey('asset.id'))
    reference_uri = Column(String)
    user_id = Column(String)
    name = Column(Unicode)
    status = Column(Enum(TaskStatus), default=TaskStatus.new)

    def get_json_d(self):
        return {
            'id': self.id,
            'assetId': self.asset_id,
            'referenceUri': self.reference_uri,
            'userId': self.user_id,
            'name': self.name,
            'status': self.status,
        }


class TaskNote(ModificationMixin, CreationMixin, RecordMixin, Base):
    __tablename__ = 'task_note'
    task_id = Column(String, ForeignKey('task.id'))
    user_id = Column(String)
    text = Column(UnicodeText)
