from os.path import join

from ..macros import load_json

from . import CONSTANTS_FOLDER


ASSET_TYPES = load_json(join(CONSTANTS_FOLDER, 'assetTypes.json'))
