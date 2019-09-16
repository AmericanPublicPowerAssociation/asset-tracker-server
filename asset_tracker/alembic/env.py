from alembic import context
from pyramid.paster import get_appsettings, setup_logging
from pyramid.settings import aslist
from sqlalchemy import engine_from_config

from asset_tracker.models import load_spatialite_sqlite_extension
from asset_tracker.models.meta import Base


config = context.config
setup_logging(config.config_file_name)
settings = get_appsettings(config.config_file_name)
target_metadata = Base.metadata
excluded_by_key = config.get_section('alembic:excluded')
excluded_tables = aslist(excluded_by_key['tables'])
excluded_indices = aslist(excluded_by_key['indices'])


def run_migrations_offline():
    context.configure(
        url=settings['sqlalchemy.url'], include_object=include_object)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    if settings['sqlalchemy.url'].startswith('sqlite'):
        load_spatialite_sqlite_extension(engine)
    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object)
    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


def include_object(object, name, type_, reflected, compare_to):
    if type_ == 'table' and name in excluded_tables:
        return False
    if type_ == 'index' and name in excluded_indices:
        return False
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
