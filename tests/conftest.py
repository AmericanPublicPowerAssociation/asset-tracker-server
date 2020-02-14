import json
from os.path import dirname, join


def load_example_json(example_name):
    example_path = join(EXAMPLES_FOLDER, example_name)
    return json.load(open(example_path, 'rt'))


TESTS_FOLDER = dirname(__file__)
EXAMPLES_FOLDER = join(TESTS_FOLDER, 'examples')
EXAMPLE_BY_NAME = {
    'basic': {
        'assets': load_example_json('assets1.json'),
        'assetsGeoJson': load_example_json('assets1.geojson'),
    },
}
pytest_plugins = [
    'asset_tracker.tests',
]
