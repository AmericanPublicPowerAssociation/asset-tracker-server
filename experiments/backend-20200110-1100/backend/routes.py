def includeme(config):
    config.add_route('hello', '/hello')
    config.add_route('home', '/')
    config.add_route('assets.json', '/assets.json')
    config.add_route('task', '/task')
    config.add_route('tasks', '/tasks')
