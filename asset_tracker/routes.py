def includeme(config):
    config.add_route('assets.json', '/assets.json')
    config.add_route('asset.json', '/assets/{asset_id}.json')
