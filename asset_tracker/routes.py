def includeme(config):
    config.add_route('assets.json', '/assets.json')
    config.add_route('asset.json', '/assets/{id}.json')
    config.add_route('asset_link.json', '/assets/{id}/{type}/{other_id}.json')
