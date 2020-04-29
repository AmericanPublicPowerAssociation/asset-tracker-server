from invisibleroads_macros_configuration import load_json
from os.path import join

from . import DATASETS_FOLDER

ASSET_TYPE_BY_CODE = load_json(join(DATASETS_FOLDER, 'assetTypeByCode.json'))
