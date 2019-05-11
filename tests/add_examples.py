from argparse import ArgumentParser
from pyramid.paster import bootstrap, setup_logging

from asset_tracker.models import Asset


def add_examples(db):
    for d in [
        {'id': 'aiJN', 'type_id': 'st', 'name': 'Transmission Substation 1'},
        {'id': 'abcd', 'type_id': 'sd', 'name': 'Distribution Substation 1'},
    ]:
        asset = Asset(**d)
        db.add(asset)


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('configuration_path')
    a = p.parse_args()
    setup_logging(a.configuration_path)
    request = bootstrap(a.configuration_path)['request']
    with request.tm:
        add_examples(request.db)
