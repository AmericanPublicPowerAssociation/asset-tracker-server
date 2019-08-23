from datetime import datetime


DATESTAMP_FORMAT = '%Y%m%d'
TIMESTAMP_FORMAT = DATESTAMP_FORMAT + '-%H%M'


def get_timestamp(x=None):
    # Adapted from invisibleroads-macros
    if x is None:
        x = datetime.now()
    return x.strftime(TIMESTAMP_FORMAT)
