from pyramid.view import view_config


@view_config(
    route_name='assetsLogs.json',
    renderer='json',
    request_method='GET')
def see_assets_logs_json(request):
    return [{
        'id': 'aa',
        'description': 'AA',
    }, {
        'id': 'bb',
        'description': 'BB',
    }]
