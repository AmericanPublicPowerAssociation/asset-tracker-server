import json


def load_json(path):
    return json.load(open(path, 'rt'))
