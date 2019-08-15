def includeme(config):
    config.add_route(
        'asset_types.json',
        '/assetTypes.json')
    config.add_route(
        'assets.json',
        '/assets.json')
    config.add_route(
        'asset.json',
        '/assets/{id}.json'),
    config.add_route(
        'asset_relation.json',
        '/assets/{id}/{key}/{otherId}.json'),
    config.add_route(
        'assets.csv',
        '/assets/')
