from alembic import context
from invisibleroads_posts.routines.configuration import load_filled_settings
from invisibleroads_records.models import Base, get_database_engine
from pyramid.settings import aslist


config = context.config
settings = load_filled_settings(config.config_file_name)
target_metadata = Base.metadata
excluded_by_key = config.get_section('alembic:excluded')
excluded_tables = aslist(excluded_by_key['tables'])
excluded_indices = aslist(excluded_by_key['indices'])


def run_migrations_offline():
    context.configure(
        url=settings['sqlalchemy.url'],
        include_object=include_object)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = get_database_engine(settings, prefix='sqlalchemy.')
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
