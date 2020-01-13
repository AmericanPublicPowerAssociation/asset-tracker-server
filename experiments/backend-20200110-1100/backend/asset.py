from pyramid.view import (
    view_config,
    view_defaults
    )


@view_defaults(
    route_name='asset',
    renderer='json')
class AssetViews:
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        query = self.request.params.get('query', 'None')
        return {'name': 'get', 'query': query}

    @view_config(request_method='PATCH')
    def patch(self):
        return {'name': 'patch'}
    
    @view_config(request_method='POST')
    def post(self):
        return {'name': 'POST'}
    
    @view_config(route_name='assets')
    def get_all_assets(self):
        return [1, 2, 3]


