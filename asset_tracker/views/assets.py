from pyramid.view import view_config


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='GET')
def see_assets_json(request):
    return {}


@view_config(
    route_name='assets.json',
    renderer='json',
    request_method='PATCH')
def change_assets_json(request):
    return {}
