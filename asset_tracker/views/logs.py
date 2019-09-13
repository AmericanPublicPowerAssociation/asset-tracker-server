from pyramid.view import view_config
from sqlalchemy import desc

from ..models import Log


@view_config(
    route_name='logs.json',
    renderer='json',
    request_method='GET')
def see_logs_json(request):
    # !!! Get logs for utilities to which user has access
    db = request.db
    logs = db.query(Log).all()
    return [_.get_json_d() for _ in logs]


@view_config(
    route_name='logs_metrics.json',
    renderer='json',
    request_method='GET')
def see_logs_metrics_json(request):
    db = request.db
    recent_logs = db.query(Log).order_by(
        desc(Log.creation_datetime)).limit(10).all()
    return {
        'recentLogs': [_.get_json_d() for _ in recent_logs],
    }
