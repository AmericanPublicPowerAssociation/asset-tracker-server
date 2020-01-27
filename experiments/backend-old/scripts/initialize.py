from pyramid.paster import bootstrap, setup_logging
from sys import argv

from asset_tracker.models import get_database_engine
from asset_tracker.models.meta import Base


configuration_path = argv[1]
setup_logging(configuration_path)
env = bootstrap(configuration_path)
settings = env['registry'].settings

database_engine = get_database_engine(settings)
Base.metadata.create_all(database_engine)
