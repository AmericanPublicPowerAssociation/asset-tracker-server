from asset_tracker.views import index


class TestIndex(object):

    def test_accept_parameters(self, application_request):
        d = index(application_request)
        assert d['text'] == 'whee!'
