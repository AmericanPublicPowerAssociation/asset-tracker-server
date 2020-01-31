def includeme(config):
    config.add_route('hello', '/hello')
    config.add_route('home', '/')
    config.add_route('asset_delete', '/assets/{id}.json')
    config.add_route('assets.json', '/assets.json')
    config.add_route('connections.json', '/connections.json')
    config.add_route('buses.json', '/buses.json')
    config.add_route('tasks.json', '/tasks.json')
