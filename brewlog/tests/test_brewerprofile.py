from flask import session
from flask_login import login_user

from brewlog import session as dbsession
from brewlog.tests import BrewlogTestCase
from brewlog.models import BrewerProfile


class BrewerProfileTestCase(BrewlogTestCase):

    def test_empty(self):
        with self.app.test_client() as client:
            rv = client.get('/')
            self.assertIn('login page', rv.data)

    def test_login(self):
        user = BrewerProfile.query.filter_by(email='user@example.com').first()
        profile_url = '/profile/%s' % user.id
        with self.app.test_client() as client:
            # check redirect
            rv = client.get('/auth/local')
            self.assertRedirects(rv, profile_url)
            # check target resource
            rv = client.get('/auth/local', follow_redirects=True)
            self.assertIn('You have been signed in as %s using local handler' % user.email, rv.data)
