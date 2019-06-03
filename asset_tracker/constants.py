import json
from os.path import dirname, join


FOLDER = dirname(__file__)
ASSET_TYPES = json.load(open(join(
    FOLDER, 'datasets', 'assetTypes.json')))
ASSET_TYPE_BY_ID = {_['id']: _ for _ in ASSET_TYPES}
RECORD_ID_LENGTH = 8
RECORD_RETRY_COUNT = 3
