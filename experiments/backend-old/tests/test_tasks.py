from asset_tracker.models import Task
from asset_tracker.views.tasks import add_task_json


class TestAddTaskJson(object):

    def test_accept_parameters(self, website_request, db):
        website_request.json_body = {
            'name': 'x',
        }
        assert db.query(Task).count() == 0
        add_task_json(website_request)
        assert db.query(Task).count() == 1
