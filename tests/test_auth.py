from flask import url_for
import pytest

from brewlog.models.users import BrewerProfile

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestAuth(BrewlogTests):

    def test_provider_selector(self):
        url = url_for('auth.select')
        rv = self.client.get(url)
        assert rv.status_code == 200
        content = rv.data.decode('utf-8')
        for x in [url_for('auth.login', provider=p) for p in ('google', 'facebook', 'local', 'github')]:
            link_text = 'href="%s"' % x
            assert link_text in content

    def test_invalid_provider_selected(self):
        provider_name = 'invalid'
        url = url_for('auth.login', provider=provider_name)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['Location']

    def test_logout(self):
        user = BrewerProfile.get_by_email('user@example.com')
        url = url_for('auth.logout')
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('home.index') in rv.headers['Location']

    def test_create_new_user_on_login(self):
        email = 'john.doe@acme.com'
        self.login(self.client, email)
        assert BrewerProfile.get_by_email(email) is not None

    def test_remote_login(self, mocker):
        provider = 'dummy'
        url = url_for('auth.login', provider=provider)
        route = mocker.sentinel.route
        fake_url_for = mocker.Mock(return_value=route)
        mocker.patch('brewlog.auth.views.url_for', fake_url_for)
        fake_redirect = mocker.Mock(return_value='redirect')
        fake_service = mocker.MagicMock(authorize_redirect=fake_redirect)
        mocker.patch.dict('brewlog.auth.views.services', {provider: fake_service})
        self.client.get(url)
        fake_redirect.assert_called_once_with(route)
