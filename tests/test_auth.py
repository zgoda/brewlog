import pytest
from flask import url_for

from brewlog.models import BrewerProfile

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestSocialAuth(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.select_url = url_for('auth.select')

    def test_provider_selector(self):
        rv = self.client.get(self.select_url)
        assert rv.status_code == 200
        urls = []
        for provider in ('google', 'facebook', 'local', 'github'):
            urls.append(url_for('auth.login', provider=provider))
        for url in urls:
            link_text = f'href="{url}"'
            assert link_text in rv.text

    def test_invalid_provider_selected(self):
        provider_name = 'invalid'
        url = url_for('auth.login', provider=provider_name)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert self.select_url in rv.headers['Location']

    def test_logout(self, user_factory):
        user = user_factory()
        url = url_for('auth.logout')
        self.login(user.email)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('home.index') in rv.headers['Location']

    def test_create_new_user_on_login(self):
        email = 'john.doe@acme.com'
        self.login(email)
        assert BrewerProfile.get_by_email(email) is not None

    def test_remote_login(self, mocker):
        provider = 'google'
        url = url_for('auth.login', provider=provider)
        route = mocker.sentinel.route
        fake_url_for = mocker.Mock(return_value=route)
        mocker.patch('brewlog.auth.views.url_for', fake_url_for)
        fake_redirect = mocker.Mock(return_value='redirect')
        fake_service = mocker.MagicMock(authorize_redirect=fake_redirect)
        mocker.patch('brewlog.auth.views.providers.google', fake_service)
        self.client.get(url)
        fake_redirect.assert_called_once_with(route)


@pytest.mark.usefixtures('client_class')
class TestRegister(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('auth.register')

    def test_anon_get(self):
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text

    def test_authenticated_get(self, user_factory):
        user = user_factory()
        login_url = url_for('auth.select')
        self.login(user.email)
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text
        assert f'href="{login_url}"' in rv.text

    def test_post_ok(self):
        data = {
            'username': 'user1',
            'password1': 'pass1',
            'password2': 'pass1',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'proceed to login' in rv.text
        assert BrewerProfile.query.filter_by(username=data['username']).count() > 0

    @pytest.mark.parametrize('data', [
        {'password1': 'pass1', 'password2': 'pass1'},
        {'username': 'user1'},
        {'username': 'user1', 'password1': 'pass1'},
        {'username': 'user1', 'password2': 'pass1'},
        {'username': 'user1', 'password1': 'pass1', 'password2': 'pass2'},
    ], ids=[
        'missing-username', 'missing-both-passwords', 'missing-pass2', 'missing-pass1',
        'passwords-differ',
    ])
    def test_post_fail(self, data):
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'proceed to login' not in rv.text
        if 'username' in data:
            assert BrewerProfile.query.filter_by(username=data['username']).count() == 0

    def test_post_username_exists(self, user_factory):
        name = 'user1'
        user_factory(username=name)
        data = {
            'username': name,
            'password1': 'password',
            'password2': 'password',
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'proceed to login' not in rv.text
        assert BrewerProfile.query.filter_by(username=name).count() == 1


@pytest.mark.usefixtures('client_class')
class TestLogin(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('auth.select')

    def test_ok_with_username(self, user_factory):
        name = 'user1'
        password = 'pass1'
        email = 'testuser@dev.brewlog.com'
        user_factory(username=name, email=email, nick=name, password=password)
        rv = self.client.post(
            self.url, data={'userid': name, 'password': password},
            follow_redirects=True,
        )
        assert f'now logged in as {name}' in rv.text

    def test_ok_with_email(self, user_factory):
        name = 'user1'
        password = 'pass1'
        email = 'testuser@dev.brewlog.com'
        user_factory(username=name, email=email, nick=name, password=password)
        rv = self.client.post(
            self.url, data={'userid': email, 'password': password},
            follow_redirects=True,
        )
        assert f'now logged in as {name}' in rv.text

    def test_fail_no_account(self):
        rv = self.client.post(
            self.url, data={'userid': 'user1', 'password': 'pass1'},
            follow_redirects=True,
        )
        assert 'user account not found or wrong password' in rv.text

    def test_fail_wrong_password(self, user_factory):
        name = 'user1'
        password = 'pass1'
        email = 'testuser@dev.brewlog.com'
        user_factory(username=name, email=email, nick=name, password=password)
        rv = self.client.post(
            self.url, data={'userid': name, 'password': 'pass2'},
            follow_redirects=True,
        )
        assert 'user account not found or wrong password' in rv.text
