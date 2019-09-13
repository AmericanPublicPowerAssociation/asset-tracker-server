import enum
from sqlalchemy import Column
from sqlalchemy.types import (
    Enum,
    PickleType,
    String)

from .meta import Base, CreationMixin, RecordMixin


class LogEvent(enum.Enum):
    add_asset = 0
    change_asset = 10
    change_asset_relation = 20
    drop_asset = 90
    import_assets_csv = 800
    export_assets_csv = 900


class Log(CreationMixin, RecordMixin, Base):
    __tablename__ = 'log'
    user_id = Column(String)
    event = Column(Enum(LogEvent))
    attributes = Column(PickleType)

    def get_json_d(self):
        return {
            'userId': self.user_id,
            'event': self.event.name,
            'timestamp': self.creation_timestamp,
            'attributes': self.attributes,
        }


def log_event(request, event, attributes):
    db = request.db
    log = Log.make_unique_record(db)
    log.user_id = request.authenticated_userid
    log.event = event
    log.attributes = attributes
