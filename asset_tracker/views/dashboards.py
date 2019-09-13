from asset_report_risks.views import see_risks_metrics_json
from pyramid.view import view_config

from .assets import see_assets_metrics_json
from .logs import see_logs_metrics_json
from .tasks import see_tasks_metrics_json


@view_config(
    route_name='dashboards.json',
    renderer='json',
    request_method='GET')
def see_dashboards_json(request):
    return {
        'assets': see_assets_metrics_json(request),
        'logs': see_logs_metrics_json(request),
        'risks': see_risks_metrics_json(request),
        'tasks': see_tasks_metrics_json(request),
    }
