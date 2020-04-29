class TestIndex(object):

    def test_accept_parameters(self, application):
        response = application.get('/', status=200)
        assert response.json == {'text': 'whee!'}
