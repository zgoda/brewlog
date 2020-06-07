from datetime import datetime

import pytest
from flask import url_for
from itsdangerous.exc import BadSignature, SignatureExpired

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

    def test_fail_incomplete_data(self, user_factory):
        name = 'user1'
        password = 'pass1'
        email = 'testuser@dev.brewlog.com'
        user_factory(username=name, email=email, nick=name, password=password)
        rv = self.client.post(
            self.url, data={'userid': name}, follow_redirects=True,
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


@pytest.mark.usefixtures('client_class')
class TestForgotPassword(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('auth.forgotpassword')

    def test_get(self):
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text

    @pytest.mark.parametrize('data', [
        {'email1': 'garbage', 'email2': 'garbage'},
        {'email1': 'user1@invalid.com', 'email2': 'user2@invalid.com'},
        {'email1': 'user1@invalid.com'}
    ], ids=['invalid', 'different', 'incomplete'])
    def test_post_invalid_data(self, data):
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert f'action="{self.url}"' in rv.text
        assert 'invalid-feedback' in rv.text

    def test_post_fail_no_user(self):
        data = {'email1': 'user1@invalid.com', 'email2': 'user1@invalid.com'}
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert all([
            'we don' in rv.text,
            't know that email' in rv.text
        ])

    def test_post_fail_unconfirmed(self, user_factory):
        user_factory(email='user1@invalid.com', password='pass', email_confirmed=False)
        data = {'email1': 'user1@invalid.com', 'email2': 'user1@invalid.com'}
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'not yet confirmed' in rv.text

    def test_post_ok(self, mocker, user_factory):
        fake_post = mocker.Mock()
        fake_requests = mocker.Mock(post=fake_post)
        mocker.patch('brewlog.tasks.requests', fake_requests)
        email = 'user1@invalid.com'
        user_factory(email=email, password='pass', email_confirmed=True)
        data = {'email1': email, 'email2': email}
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'message with password reset instructions has been sent' in rv.text
        _, _, kw = fake_post.mock_calls[0]
        mail_data = kw['data']
        assert email in mail_data['to']
        assert len(mail_data['to']) == 1
        assert 'reset password' in mail_data['subject']

    def test_post_task_exc(self, caplog, mocker, user_factory):
        fake_post = mocker.Mock(side_effect=Exception)
        fake_requests = mocker.Mock(post=fake_post)
        mocker.patch('brewlog.tasks.requests', fake_requests)
        user_factory(email='user1@invalid.com', password='pass', email_confirmed=True)
        data = {'email1': 'user1@invalid.com', 'email2': 'user1@invalid.com'}
        self.client.post(self.url, data=data, follow_redirects=True)
        assert 'exception in background task' in caplog.text


@pytest.mark.usefixtures('client_class')
class TestResetPassword(BrewlogTests):

    def url(self, token):
        return url_for('auth.resetpassword', token=token)

    def test_get_ok(self, mocker, user_factory):
        user = user_factory()
        fake_serializer = mocker.MagicMock(
            loads=mocker.Mock(return_value={'id': user.id})
        )
        mocker.patch(
            'brewlog.utils.views.URLSafeTimedSerializer',
            mocker.Mock(return_value=fake_serializer),
        )
        url = self.url(token='fake_token')
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    def test_get_fail_signature_expired(self, mocker):
        signed = datetime(2019, 11, 11, 14, 22, 16)
        fake_serializer = mocker.MagicMock(
            loads=mocker.Mock(
                side_effect=SignatureExpired(message='Fail', date_signed=signed)
            )
        )
        mocker.patch(
            'brewlog.utils.views.URLSafeTimedSerializer',
            mocker.Mock(return_value=fake_serializer),
        )
        url = self.url(token='fake_token')
        rv = self.client.get(url, follow_redirects=True)
        assert 'token expired' in rv.text

    def test_get_fail_signature_tampered(self, mocker):
        fake_serializer = mocker.MagicMock(
            loads=mocker.Mock(side_effect=BadSignature(message='Fail'))
        )
        mocker.patch(
            'brewlog.utils.views.URLSafeTimedSerializer',
            mocker.Mock(return_value=fake_serializer),
        )
        url = self.url(token='fake_token')
        rv = self.client.get(url, follow_redirects=True)
        assert 'invalid token' in rv.text

    def test_get_fail_user_not_found(self, mocker, user_factory):
        user = user_factory()
        fake_serializer = mocker.MagicMock(
            loads=mocker.Mock(return_value={'id': user.id + 1})
        )
        mocker.patch(
            'brewlog.utils.views.URLSafeTimedSerializer',
            mocker.Mock(return_value=fake_serializer),
        )
        url = self.url(token='fake_token')
        rv = self.client.get(url)
        assert rv.status_code == 400

    def test_post_ok(self, mocker, user_factory):
        user = user_factory()
        fake_serializer = mocker.MagicMock(
            loads=mocker.Mock(return_value={'id': user.id})
        )
        mocker.patch(
            'brewlog.utils.views.URLSafeTimedSerializer',
            mocker.Mock(return_value=fake_serializer),
        )
        url = self.url(token='fake_token')
        data = {
            'new_password': 'test',
            'new_password_r': 'test'
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'your password has been changed' in rv.text
