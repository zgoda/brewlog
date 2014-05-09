from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models.users import BrewerProfile


class AuthTestCase(BrewlogTestCase):

    def test_provider_selector(self):
        url = url_for('auth-select-provider')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            for x in [url_for('auth-login', provider=p) for p in ('google', 'facebook', 'local', 'github')]:
                self.assertIn('href="%s"' % x, rv.data)

    def test_invalid_provider_selected(self):
        provider_name = 'invalid'
        url = url_for('auth-login', provider=provider_name)
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertEqual(rv.status_code, 302)
            self.assertIn(url_for('auth-select-provider'), rv.headers['Location'])

    def test_logout(self):
        user = BrewerProfile.get_by_email('user@example.com')
        url = url_for('auth-logout')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 302)
            self.assertIn(url_for('main'), rv.headers['Location'])

    def test_create_new_user_on_login(self):
        email = 'john.doe@acme.com'
        with self.app.test_client() as client:
            self.login(client, email)
            self.assertIsNotNone(BrewerProfile.get_by_email(email))
