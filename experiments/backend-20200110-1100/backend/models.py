import enum
from sqlalchemy.orm import sessionmaker, configure_mappers, relationship
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
from sqlalchemy.types import (PickleType, String, Boolean,
    Enum, Unicode, UnicodeText)


import zope.sqlalchemy


# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.zzzcomputing.com/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
# Define declarative base here
Base = declarative_base(metadata=metadata)


# Define your classes
class Asset(Base):
    __tablename__ = 'asset'
    id = Column(String, primary_key=True)
    name = Column(String)
    type_code = Column(String)
    attributes = Column(PickleType)
    connections = relationship('Connection')
    deleted = Column('deleted', Boolean(name='deleted_bool'), default=False)
    json_required_field = [('name', str), ('type_code', str)]

    def __repr__(self):
        return f'<Asset({self.id})>'

    def get_json_d(self):
        d = dict(self.attributes or {}, **{
            'id': self.id,
            'name': self.name,
            'type_code': self.type_code,
            'busByIndex': {_.id: _.get_json_d() for _ in self.connections}
        })
        return d

    @classmethod
    def make_asset_from_json(cls, json):
        for column, d_type in cls.json_required_field:
            if not isinstance(column, d_type):
                return None
        # returns one asset
        pass

    @classmethod
    def update_from_json_list(cls, old_asset, updated_asset):
        # returns updated data
        pass


class Bus(Base):
    __tablename__ = 'bus'
    id = Column(String, primary_key=True)


class Connection(Base):
    __tablename__ = 'connection'
    asset_id = Column(String, ForeignKey('asset.id'), primary_key=True)
    bus_id = Column(String, ForeignKey('bus.id'), primary_key=True)
    attributes = Column(PickleType)

    def get_json_d(self):
        return dict(self.attributes or {}, **{
            'busId': self.asset_id,
            'attributes': self.attributes
        })

    def __repr__(self):
        argument_string = ', '.join((
            f'asset_id={self.asset_id}',
            f'bus_id={self.bus_id}',
        ))
        return f'<Connection({argument_string})>'


class LineType(Base):
    __tablename__ = 'line_type'
    id = Column(String, primary_key=True)
    attributes = Column(PickleType)


class TaskStatus(enum.Enum):
    Cancelled = -100
    New = 0
    Pending = 50
    Done = 100


class Task(Base):
    __tablename__ = 'task'
    id = Column(String, primary_key=True)
    asset_id = Column(String, ForeignKey('asset.id'))
    asset = relationship('Asset', backref='tasks')
    reference_uri = Column(String)
    name = Column(Unicode)
    status = Column(Enum(TaskStatus), default=TaskStatus.New)
    creation_user_id = Column(String)
    assignment_user_id = Column(String)

    def get_json_d(self):
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


# Configures transaction manager
# Configure database session factory
def get_tm_session(session_factory, transaction_manager):
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    config.include('pyramid_tm')
    settings = config.get_settings()
    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.create_all(engine)
    session_factory = sessionmaker()
    session_factory.configure(bind=engine)
    config.registry['dbsession_factory'] = session_factory

    # Configure request.db so you can access the database
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'db',
        reify=True)


configure_mappers()
