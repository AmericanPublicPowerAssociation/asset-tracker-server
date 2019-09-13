from pyramid.view import view_config

# from ..models import Log


@view_config(
    route_name='logs.json',
    renderer='json',
    request_method='GET')
def see_logs_json(request):
    # !!! Get logs for utilities to which user has access
    return []


@view_config(
    route_name='logs_metrics.json',
    renderer='json',
    request_method='GET')
def see_logs_metrics_json(request):
    return {}
