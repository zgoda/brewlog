from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models import BrewerProfile


class BrewerProfileTestCase(BrewlogTestCase):

    def test_login(self):
        user = BrewerProfile.get_by_email('user@example.com')
        profile_url = url_for('profile-details', userid=user.id)
        with self.app.test_client() as client:
            # check redirect
            rv = client.get(url_for('auth-login', provider='local'), follow_redirects=False)
            self.assertRedirects(rv, profile_url)
            # check target resource
            rv = self.login(client, user.email)
            self.assertIn('You have been signed in as %s using local handler' % user.email, rv.data)

    def test_anon_view_profile(self):
        user = BrewerProfile.get_by_email('user@example.com')
        profile_url = url_for('profile-details', userid=user.id)
        with self.app.test_client() as client:
            rv = client.get(profile_url)
            self.assertNotIn('form', rv.data)

    def test_update_other_profile(self):
        user1 = BrewerProfile.get_by_email('user1@example.com')
        user2 = BrewerProfile.get_by_email('user2@example.com')
        profile_url = url_for('profile-details', userid=user1.id)
        with self.app.test_client() as client:
            self.login(client, user2.email)
            data = {
                'nick': 'new nick',
            }
            rv = client.post(profile_url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_update_by_anon(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile-details', userid=user.id)
        with self.app.test_client() as client:
            data = {
                'nick': 'new nick',
            }
            rv = client.post(profile_url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_update_by_self(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile-details', userid=user.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            data = {
                'nick': 'Stephan',
                'email': user.email,
            }
            rv = client.post(profile_url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(BrewerProfile.get_by_email(user.email).nick, data['nick'])
