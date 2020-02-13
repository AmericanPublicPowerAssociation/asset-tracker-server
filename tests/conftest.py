import json
from os.path import dirname, join

from asset_tracker.constants import PACKAGE_FOLDER


def load_dataset_json(dataset_name):
    dataset_path = join(DATASETS_FOLDER, dataset_name)
    return json.load(open(dataset_path, 'rt'))


REPOSITORY_FOLDER = dirname(PACKAGE_FOLDER)
DATASETS_FOLDER = join(REPOSITORY_FOLDER, 'datasets')
EXAMPLE_BY_NAME = {
    'basic': {
        'assets': load_dataset_json('assets1.json'),
        'assetsGeoJson': load_dataset_json('assets1.geojson'),
    },
}
