import enum
from sqlalchemy import Column
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import (
    Enum,
    PickleType,
    String)

from .meta import Base, CreationMixin, ModificationMixin, RecordMixin


class AssetStatus(enum.Enum):
    Broken = -100
    Planned = 0
    Installing = 25
    Repairing = 50
    Operational = 100


class Asset(ModificationMixin, CreationMixin, RecordMixin, Base):
    __table_args__ = (
        UniqueConstraint(
            'utility_id', 'name', name='unique_utility_asset_name'),
    )
    utility_id = Column(String)
    status = Column(Enum(AssetStatus), default=AssetStatus.Operational)
    shape = Column(PickleType, default={})

    @property
    def can_be_mass_produced(self):
        return not self.primary_type.get('unique', False)

    @property
    def is_power_source(self):
        return self.is_in_substation or self.is_in_station

    @property
    def is_in_station(self):
        return self.has_parent_type_id('S')

    @property
    def is_in_substation(self):
        return self.has_parent_type_id('s')

    def is_readable(self, request):
        return True

    def is_editable(self, request):
        return True

    @classmethod
    def get_readable_ids(Class, request):
        db = request.db
        # !!! Limit to asset ids that the user has permission to view
        return [_[0] for _ in db.query(Class.id)]
