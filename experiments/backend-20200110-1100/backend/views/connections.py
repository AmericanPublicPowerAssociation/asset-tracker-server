from pyramid.view import (
    view_config,
    view_defaults
    )
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm import selectinload
from backend.models import (Connection)


@view_defaults(
    route_name='connections.json',
    renderer='json')
class ConnectionsViews:

    @view_config(request_method='GET')
    def get(self):
        connections = self.query
        return [_.get_json_d() for _ in connections]

    @view_config(request_method='PATCH')
    def patch(self):
        pass

    @view_config(request_method='POST')
    def post(self):
        pass

    @view_config(request_method='DELETE')
    def delete(self):
        pass
