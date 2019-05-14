'''
import transaction
import unittest
from pyramid.testing import (
    # DummyRequest,
    setUp,
    tearDown)

from .models import (
    Base,
    get_database_engine,
    get_database_session_factory,
    get_transaction_manager_session)


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.config = setUp(settings={'sqlalchemy.url': 'sqlite:///:memory:'})
        self.config.include('.models')
        settings = self.config.get_settings()
        self.engine = get_database_engine(settings)
        session_factory = get_database_session_factory(self.engine)
        self.session = get_transaction_manager_session(
            session_factory, transaction.manager)

    def initialize_database(self):
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from .models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'Asset Tracker')


class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)


def dummy_request(db):
    return DummyRequest(db=db)
'''
