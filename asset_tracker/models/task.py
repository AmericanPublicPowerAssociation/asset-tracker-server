import enum
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import (
    Enum,
    String,
    Unicode,
    UnicodeText)

from .meta import Base, CreationMixin, ModificationMixin, RecordMixin


class TaskStatus(enum.Enum):
    CANCELLED = -1
    NEW = 0
    PENDING = 10
    DONE = 100


class TaskPriority(enum.Enum):
    HIGH = 1
    NORMAL = 10
    LOW = 100


class Task(ModificationMixin, CreationMixin, RecordMixin, Base):
    __tablename__ = 'task'
    asset_id = Column(String, ForeignKey('asset.id'))
    asset = relationship('Asset', backref='tasks')
    reference_uri = Column(String)
    name = Column(Unicode)
    status = Column(Enum(TaskStatus), default=TaskStatus.NEW)
    priority = Column(Enum(TaskPriority), default=TaskPriority.NORMAL)
    creation_user_id = Column(String)
    assignment_user_id = Column(String)

    def get_json_dictionary(self):
        return {
            'id': self.id,
            'assetId': self.asset_id,
            'assetName': self.asset.name,
            'referenceUri': self.reference_uri,
            'name': self.name,
            'status': self.status.value,
            'creationUserId': self.creation_user_id,
            'assignmentUserId': self.assignment_user_id,
        }


class TaskComment(ModificationMixin, CreationMixin, RecordMixin, Base):
    __tablename__ = 'task_comment'
    task_id = Column(String, ForeignKey('task.id'))
    user_id = Column(String)
    text = Column(UnicodeText)
