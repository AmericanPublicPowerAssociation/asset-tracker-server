from logging import NullHandler, getLogger


def get_log(name):
    # Adapted from invisibleroads-macros
    log = getLogger(name)
    log.addHandler(NullHandler())
    return log
