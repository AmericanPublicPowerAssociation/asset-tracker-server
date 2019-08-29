import json
from cgi import FieldStorage
# from functools import partial
# from sqlite3 import IntegrityError

import numpy as np
import pandas as pd
import shapely.wkt as wkt
from pyramid.httpexceptions import (
    HTTPBadRequest, HTTPInsufficientStorage, HTTPNotFound)
from pyramid.response import Response
from pyramid.view import view_config

from asset_tracker.utils.data import (
    restore_array_to_csv,
    get_extra_columns_df,
    build_flat_dict_structure,
    transform_array_to_csv)
# from asset_tracker.validations.tasks import validate_tasks_df

# from ..constants import ASSET_TYPES
# from ..constants import TASKS_STATUS

from ..exceptions import DatabaseRecordError
from ..macros.text import normalize_text
# from ..models import Asset
from ..models import AssetTask


def see_tasks(request):
    db = request.db
    return db.query(AssetTask).all()


@view_config(
    route_name='tasks.json',
    renderer='json',
    request_method='GET')
def see_tasks_json(request):
    tasks = see_tasks(request)
    return [_.serialize() for _ in tasks]


@view_config(
    route_name='tasks.json',
    renderer='json',
    request_method='POST')
def add_task_json(request):
    params = request.json_body
    try:
        asset_id = params['assetId']
    except KeyError:
        raise HTTPBadRequest({'assetId': 'is required'})
    #!!! check valid asset id
    try:
        user_id = params['usereId']
    except KeyError:
        raise HTTPBadRequest({'usereId': 'is required'})
    #!!! check valid user id
    try:
        reference_id = params['referenceId']
    except KeyError:
        raise HTTPBadRequest({'referenceId': 'is required'})
    # !!! check valid reference id
    # !!! check whether user can add tasks to reference id
    
    db = request.db
    try:
        name = params['name']
    except KeyError:
        # !!! consider filling task name automatically
        raise HTTPBadRequest({'name': 'is required'})
    else:
        name = validate_name(db, name, reference_id)
    try:
        status = params['status']
    except KeyError:
        raise HTTPBadRequest({'status': 'is required'})
    # !!! check valid status
    try:
        description = params['description']
    except KeyError:
        raise HTTPBadRequest({'description': 'is required'})
    try:
        task = AssetTask.make_unique_record(db)
    except DatabaseRecordError:
        raise HTTPInsufficientStorage({'task': 'could not make unique id'})
    task.asset_id = asset_id
    task.user_id = user_id
    task.reference_id = reference_id
    task.name = name
    task.status = status
    return task.serialize()


@view_config(
    route_name='task.json',
    renderer='json',
    request_method='PATCH')
def change_task_json(request):
    matchdict = request.matchdict
    params = dict(request.json_body)
    db = request.db

    id = matchdict['id']
    task = db.query(AssetTask).get(id)
    if not task:
        raise HTTPNotFound({'id': 'does not exist'})
    changed_tasks = [task]

    reference_id = task.reference_id

    # !!! Check whether user can update this task

    try:
        name = params.pop('name')
    except KeyError:
        pass
    else:
        task.name = validate_name(db, name, reference_id, id)

    params.pop('id', None)
    params.pop('assetId', None)
    params.pop('referenceId', None)
    params.pop('userId', None)
    params.pop('status', None)
    params.pop('description', None)

    return [_.serialize() for _ in changed_tasks]


# @view_config(
#     route_name='task.json',
#     renderer='json',
#     request_method='DELETE')
# def drop_task_json(request):
#     return {}





def validate_name(db, name, reference_id, id=None):
    name = normalize_text(name)
    if not name:
        raise HTTPBadRequest({'name': 'cannot be empty'})
    duplicate_query = db.query(AssetTask).filter(
        AssetTask.reference_id == reference_id, AssetTask.name.ilike(name))
    if id:
        duplicate_query = duplicate_query.filter(AssetTask.id != id)
    if duplicate_query.count():
        raise HTTPBadRequest({'name': 'must be unique within utility'})
    return name
