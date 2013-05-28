from flask import session
from flask_login import login_user

from brewlog import session as dbsession
from brewlog.tests import BrewlogTestCase
from brewlog.models import BrewerProfile


class BrewerProfileTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewerProfileTestCase, self).setUp()
        self.client = self.app.test_client()

    def test_create(self):
        user = BrewerProfile(email='test@example.com', nick='test')
        dbsession.add(user)
        dbsession.commit()
        login_user(user)
        rv = self.client.get('/profile/1')
        self.assertIn('form', rv.data)
