def includeme(config):
    config.add_route(
        'assets.json',
        '/assets.json')
    config.add_route(
        'assets.csv',
        '/assets.csv')
