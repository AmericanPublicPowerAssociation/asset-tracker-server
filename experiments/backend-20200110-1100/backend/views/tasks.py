from pyramid.view import (
    view_config,
    view_defaults
    )
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm import selectinload
from backend.models import (Task)


@view_defaults(
    route_name='tasks.json',
    renderer='json')
class TasksViews:
    def __init__(self, request):
        self.request = request

    @property
    def query(self):
        return self.request.db.query(Task)

    @view_config(request_method='GET')
    def get(self):
        tasks = query
        return [_.get_json_d() for _ in tasks]

    @view_config(request_method='PATCH')
    def patch(self):
        return {'name': 'patch'}

    @view_config(request_method='POST')
    def post(self):
        return {'name': 'post'}

    @view_config(request_method='DELETE')
    def delete(self):
        return {'name': 'delete'}
