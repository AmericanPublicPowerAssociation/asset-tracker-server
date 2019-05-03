from . import models


def setup(env):
    request = env['request']
    request.tm.begin()
    env['tm'] = request.tm
    env['db'] = request.db
    env['models'] = models
