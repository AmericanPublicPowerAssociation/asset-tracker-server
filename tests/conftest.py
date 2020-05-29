from os.path import dirname, join
from invisibleroads_macros_configuration import load_json


def load_example_json(example_name):
    return load_json(join(EXAMPLES_FOLDER, example_name))


def get_asset_dictionaries(asset_dictionary_by_id):
    asset_dictionaries = []
    for asset_id, asset_dictionary in asset_dictionary_by_id.items():
        asset_dictionary['id'] = asset_id
        asset_dictionaries.append(asset_dictionary)
    return asset_dictionaries


TESTS_FOLDER = dirname(__file__)
EXAMPLES_FOLDER = join(TESTS_FOLDER, 'examples')
EXAMPLE_BY_NAME = {
    'basic': {
        'assetById': load_example_json(join('basic', 'assetById.json')),
        'assetsGeoJson': load_example_json(join('basic', 'assets.geojson')),
    },
}

pytest_plugins = [
    'invisibleroads_posts.tests',
    'invisibleroads_records.tests',
    'asset_tracker.tests',
]
