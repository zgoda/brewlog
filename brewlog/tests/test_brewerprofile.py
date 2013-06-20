from flask import session
from flask_login import login_user

from brewlog import session as dbsession
from brewlog.tests import BrewlogTestCase
from brewlog.models import BrewerProfile


class BrewerProfileTestCase(BrewlogTestCase):

    def test_empty(self):
        rv = self.client.get('/')
        self.assertIn('strona logowania', rv.data)

