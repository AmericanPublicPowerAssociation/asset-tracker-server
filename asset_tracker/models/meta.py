import pendulum
from datetime import datetime
from invisibleroads_macros_log import get_timestamp
from invisibleroads_macros_security import make_random_string
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy.types import (
    DateTime,
    String)

from ..constants.database import (
    NAMING_CONVENTION,
    RECORD_ID_LENGTH,
    RECORD_RETRY_COUNT)
from ..exceptions import DatabaseRecordError


class RecordMixin(object):
    # Adapted from invisibleroads-records

    id = Column(String, primary_key=True)
    id_length = RECORD_ID_LENGTH

    @classmethod
    def make_unique_record(Class, database, retry_count=RECORD_RETRY_COUNT):
        count = 0
        id_length = Class.id_length
        while count < retry_count:
            record = Class(id=make_random_string(id_length))
            database.add(record)
            try:
                database.flush()
            except IntegrityError:
                database.rollback()
            else:
                break
            count += 1
        else:
            raise DatabaseRecordError(
                f'could not make unique {Class.__tablename__}')
        return record


class CreationMixin(object):
    # Adapted from invisibleroads-records

    creation_datetime = Column(DateTime, default=datetime.utcnow)

    @property
    def creation_timestamp(self):
        return get_timestamp(self.creation_datetime)

    @property
    def creation_when(self):
        return pendulum.instance(self.creation_datetime).diff_for_humans()

    @classmethod
    def get_datetime(Class):
        return Class.creation_datetime


class ModificationMixin(object):
    # Adapted from invisibleroads-records

    modification_datetime = Column(DateTime)

    @property
    def modification_timestamp(self):
        return get_timestamp(self.modification_datetime)

    @property
    def modification_when(self):
        return pendulum.instance(self.modification_datetime).diff_for_humans()

    @classmethod
    def get_datetime(Class):
        return Class.modification_datetime



CLASS_REGISTRY = {}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(class_registry=CLASS_REGISTRY, metadata=metadata)
