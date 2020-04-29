from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy import Column
from sqlalchemy.types import (
    Boolean,
    PickleType)


class DeletionMixin(object):

    is_deleted = Column(Boolean(name='is_deleted'), default=False)


class AttributesMixin(object):

    _attributes = Column(PickleType)

    @property
    def attributes(self):
        value = self._attributes
        # Return {} if value is None
        return value or {}

    @attributes.setter
    def attributes(self, value):
        # Store None if value is {}
        self._attributes = value or None


class GeometryMixin(object):

    # _geometry = Column(Geometry)  # PostgreSQL
    _geometry = Column(Geometry(management=True))  # SQLite

    @property
    def geometry(self):
        value = self._geometry
        if value is None:
            return
        return to_shape(value)

    @geometry.setter
    def geometry(self, value):
        if value is not None:
            value = from_shape(value)
        self._geometry = value
