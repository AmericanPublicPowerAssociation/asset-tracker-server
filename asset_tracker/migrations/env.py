from alembic import context
from invisibleroads_posts.routines.configuration import load_filled_settings
from invisibleroads_records.models import Base, get_database_engine


config = context.config
settings = load_filled_settings(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings['sqlalchemy.url'])
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = get_database_engine(settings, prefix='sqlalchemy.')
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
