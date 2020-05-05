from os.path import dirname, join
from invisibleroads_macros_configuration import load_json


def load_example_json(example_name):
    return load_json(join(EXAMPLES_FOLDER, example_name))


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
