from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInsufficientStorage,
    HTTPNotFound)
from pyramid.view import view_config
from sqlalchemy import desc

from ..exceptions import DatabaseRecordError
from ..macros.text import normalize_text
from ..models import Asset, Task


@view_config(
    route_name='tasks.json',
    renderer='json',
    request_method='GET')
def see_tasks_json(request):
    db = request.db
    tasks = db.query(Task)
    return [_.get_json_d() for _ in tasks]


@view_config(
    route_name='tasks_metrics.json',
    renderer='json',
    request_method='GET')
def see_tasks_metrics_json(request):
    db = request.db
    recent_tasks = db.query(Task).order_by(
        desc(Task.creation_datetime)).limit(10).all()
    return {
        'recentTasks': [_.get_json_d() for _ in recent_tasks],
    }


@view_config(
    route_name='tasks.json',
    renderer='json',
    request_method='POST')
def add_task_json(request):
    params = request.json_body
    db = request.db

    try:
        name = params['name']
    except KeyError:
        raise HTTPBadRequest({'name': 'is required'})
    else:
        name = validate_name(name)

    try:
        asset_id = params['assetId']
    except KeyError:
        raise HTTPBadRequest({'assetId': 'is required'})
    # asset_id = db.query(Asset.id).filter(Asset.id == asset_id).first()
    asset = db.query(Asset).get(asset_id)
    if not asset:
        raise HTTPBadRequest({'assetId': 'does not exist'})

    db = request.db
    try:
        task = Task.make_unique_record(db)
    except DatabaseRecordError:
        raise HTTPInsufficientStorage({'task': 'could not make unique id'})

    user_id = request.authenticated_userid
    task.asset_id = asset_id
    task.reference_uri = params.get('referenceUri')
    task.name = name
    task.creation_user_id = user_id
    task.assignment_user_id = user_id

    return task.get_json_d()


@view_config(
    route_name='task.json',
    renderer='json',
    request_method='PATCH')
def change_task_json(request):
    matchdict = request.matchdict
    params = dict(request.json_body)
    db = request.db

    id = matchdict['id']
    task = db.query(Task).get(id)
    if not task:
        raise HTTPNotFound({'id': 'does not exist'})

    # !!! Check whether user can update this task

    try:
        name = params.pop('name')
    except KeyError:
        pass
    else:
        task.name = validate_name(name)

    return task.get_json_d()


@view_config(
    route_name='task.json',
    renderer='json',
    request_method='DELETE')
def drop_task_json(request):
    return {}


def validate_name(name):
    name = normalize_text(name)
    if not name:
        raise HTTPBadRequest({'name': 'cannot be empty'})
    return name
