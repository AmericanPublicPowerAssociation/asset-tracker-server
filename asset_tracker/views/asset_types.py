from pyramid.view import view_config

from ..constants import ASSET_TYPES


@view_config(
    route_name='asset_types.json',
    renderer='json',
    request_method='GET')
def see_asset_types(request):
    return ASSET_TYPES
