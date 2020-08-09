from alembic import context
from invisibleroads_records.models import Base
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config


config = context.config
setup_logging(config.config_file_name)
settings = get_appsettings(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings['sqlalchemy.url'])
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    connection = engine.connect()
    context.configure(connection=connection, target_metadata=target_metadata)
    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
