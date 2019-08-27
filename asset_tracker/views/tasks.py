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
# from ..routines.geometry import get_bounding_box


# @view_config(
#     route_name='task_status.json',
#     renderer='json',
#     request_method='GET')
# def see_task_status_json(request):
#     return TASKS_STATUS


# @view_config(
#     route_name='tasks_kit.json',
#     renderer='json',
#     request_method='GET')
# def see_tasks_kit_json(request):
#     tasks = see_tasks(request)
#     bounding_box = get_bounding_box(tasks)
#     return {
#         'taskStatus': see_task_status_json(request),
#         'tasks': [_.serialize() for _ in tasks],
#         'boundingBox': bounding_box,
#     }


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


# @view_config(
#     route_name='task_relation.json',
#     renderer='json',
#     request_method='PATCH')
# @view_config(
#     route_name='task_relation.json',
#     renderer='json',
#     request_method='DELETE')
# def change_task_relation_json(request):
#     matchdict = request.matchdict
#     db = request.db
#     method = request.method

#     id = matchdict['id']
#     task = db.query(AssetTask).get(id)
#     if not task:
#         raise HTTPNotFound({'id': 'does not exist'})

#     other_id = matchdict['otherId']
#     other_task = db.query(AssetTask).get(other_id)
#     if not other_task:
#         raise HTTPNotFound({'otherId': 'does not exist'})

#     # !!! Check edit permissions for both tasks

#     key = matchdict['key']
#     if 'childIds' == key:
#         if method == 'PATCH':
#             task.add_child(other_task)
#         elif method == 'DELETE':
#             task.remove_child(other_task)
#     elif 'parentIds' == key:
#         if method == 'PATCH':
#             other_task.add_child(task)
#         elif method == 'DELETE':
#             other_task.remove_child(task)
#     elif 'connectedIds' == key:
#         if method == 'PATCH':
#             task.add_connection(other_task)
#         elif method == 'DELETE':
#             task.remove_connection(other_task)
#     else:
#         raise HTTPBadRequest({'key': 'is not recognized'})

#     changed_tasks = [task] + task.parents + task.children
#     return [_.serialize() for _ in changed_tasks]


# @view_config(
#     route_name='tasks.csv',
#     # renderer='',
#     request_method='GET')
# def see_tasks_csv(request):
#     db = request.db
#     tasks = db.query(Task)
#     order_columns = [
#         'id', 'utilityId', 'typeId', 'name',
#         'vendorName', 'productName', 'productVersion',
#         'KV', 'KW', 'KWH',
#         'location', 'wkt',
#         'parentIds', 'childIds', 'connectedIds',
#     ]
#     csv = ','.join(order_columns)

#     if tasks.count() > 0:
#         tasks = [build_flat_dict_structure(task) for task in tasks]
#         data = pd.read_json(json.dumps(tasks))
#         transform_array_to_csv(data, 'location')
#         transform_array_to_csv(data, 'childIds', sep=' ')
#         transform_array_to_csv(data, 'parentIds', sep=' ')
#         transform_array_to_csv(data, 'connectedIds', sep=' ')
#         csv = data[order_columns].to_csv(index=False)

#     return Response(
#         body=csv,
#         status=200,
#         content_type='text/csv',
#         content_disposition='attachment')


# @view_config(
#     route_name='tasks.csv',
#     renderer='json',
#     # request_method='PATCH',
#     request_method='POST')
# def upload_tasks_file(request):
#     file = request.POST.get('file', None)

#     if not isinstance(file, FieldStorage):
#         raise HTTPBadRequest({
#             'file': 'is required'})

#     validated_tasks, errors = validate_tasks_df(pd.read_csv(file.file))

#     if errors:
#         raise HTTPBadRequest(errors)

#     restore_array_to_csv(validated_tasks, 'location', cast=float)
#     restore_array_to_csv(validated_tasks, 'childIds', sep=' ')
#     restore_array_to_csv(validated_tasks, 'parentIds', sep=' ')
#     restore_array_to_csv(validated_tasks, 'connectedIds', sep=' ')

#     db = request.db

#     # TODO: move this logic to model or helper function
#     extra_columns = get_extra_columns_df(validated_tasks, [
#         'id',
#         'utilityId',
#         'typeId',
#         'name',
#         'parentIds',
#         'childIds',
#         'connectedIds',
#         'wkt',
#         'location',
#         'geometry',
#     ])
#     for name, row in validated_tasks.iterrows():
#         task = db.query(Task).get(row['id'])
#         if task:
#             continue

#         task = Task(id=row['id'])
#         task.reference_id = row['utilityId']
#         task.type_id = row['typeId']
#         task.name = row['name']
#         if len(row['location']) == 2:
#             task.location = row['location']
#         extra = {}
#         for column in extra_columns:
#             value = row[column]
#             if isinstance(value, float) and np.isnan(value):
#                 continue
#             extra[column] = value

#         task.attributes = extra
#         geometry = row['wkt']
#         if not (isinstance(geometry, float) and np.isnan(geometry)):
#             task.geometry = wkt.loads(geometry)

#         db.add(task)

#     for name, row in validated_tasks.iterrows():
#         task = db.query(Task).get(row['id'])

#         for child_id in row['childIds']:
#             child = db.query(Task).get(child_id)
#             if child:
#                 task.add_child(child)

#         for connected_id in row['connectedIds']:
#             connected = db.query(Task).get(connected_id)
#             if connected:
#                 task.add_connection(connected)

#     try:
#         db.flush()
#     except Exception:
#         db.rollback()

#     return {
#         'error': False
#     }


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
