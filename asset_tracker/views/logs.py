from pyramid.view import view_config


@view_config(
    route_name='logs.json',
    renderer='json',
    request_method='GET')
def see_logs_json(request):
    return []
