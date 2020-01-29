from pyramid.view import (
    view_config,
    view_defaults
    )
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm import selectinload
from backend.models import (Bus)


@view_defaults(
    route_name='buses.json',
    renderer='json')
class BusesViews:
    def __init__(self):
        self.request = request

    @property
    def query(self):
        return self.request.query(Bus)

    @view_config(request_method='GET')
    def get(self):
        buses = db.query(Bus)
        return [_.id for _ in buses]

    @view_config(request_method='PATCH')
    def patch(self):
        # TODO
        raise HTTPBadRequest('not available')

    @view_config(request_method='POST')
    def post(self):
        bus = Bus()
        self.request.db.add(bus)
        return {'status': 'ok'}

    @view_config(request_method='DELETE')
    def delete(self):
        # TODO
        raise HTTPBadRequest('not available')
