from flask_login import login_user

from brewlog import session
from brewlog.tests import BrewlogTestCase
from brewlog.models import BrewerProfile


class BrewerProfileTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewerProfileTestCase, self).setUp()
        self.client = self.app.test_client()

    def test_create(self):
        user = BrewerProfile(email='test@example.com')
        session.add(user)
        session.commit()
        login_user(user, force=True)
        rv = self.client.get('/profile/1')
        import ipdb; ipdb.set_trace()
        self.assertContext('user', user)
