import pytest
from flask import url_for

from brewlog.ext import db
from brewlog.models import BrewerProfile

from . import BrewlogTests


class BrewerProfileTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory, brew_factory):
        self.public_user = user_factory(first_name='Aaaa', last_name='Aaaa')
        self.public_brewery = brewery_factory(brewer=self.public_user, name='public brewery no 1')
        self.pb_public_brew = brew_factory(brewery=self.public_brewery, name='public brew no 1')
        self.pb_hidden_brew = brew_factory(brewery=self.public_brewery, is_public=False, name='hidden brew no 1')
        self.hidden_user = user_factory(is_public=False, first_name='Bbbb', last_name='Bbbb')
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user, name='hidden brewery no 1')
        self.hb_public_brew = brew_factory(brewery=self.hidden_brewery, name='hidden brew no 2')
        self.hb_hidden_brew = brew_factory(brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2')


@pytest.mark.usefixtures('client_class')
class TestBrewerProfileModel(BrewerProfileTests):

    def test_no_names(self, user_factory):
        user = user_factory(first_name=None, last_name=None, nick=None)
        assert 'anonymous' in user.name

    def test_last_created_public_only(self):
        assert len(BrewerProfile.last_created(public_only=True)) == 1

    def test_last_created_all(self):
        assert len(BrewerProfile.last_created(public_only=False)) == 2

    def test_public_ordering(self, user_factory):
        user = user_factory(first_name='Xxxx', last_name='Xxxx')
        assert BrewerProfile.public().first() == self.public_user
        assert BrewerProfile.public(order_by=BrewerProfile.first_name).first() == self.public_user
        assert BrewerProfile.public(order_by=db.desc(BrewerProfile.first_name)).first() == user


@pytest.mark.usefixtures('client_class')
class TestBrewerProfile(BrewerProfileTests):

    def test_login(self):
        # check redirect
        rv = self.client.get(url_for('auth.login', provider='local'), follow_redirects=False)
        assert 'localhost' in rv.headers.get('Location')
        # check target resource
        rv = self.login(self.public_user.email)
        assert f'You have been signed in as {self.public_user.email}' in rv.data.decode('utf-8')

    def test_hidden_user(self):
        rv = self.client.get(url_for('home.index'))
        assert self.hidden_user.full_name not in rv.data.decode('utf-8')

    def test_view_list_by_public(self):
        url = url_for('profile.all')
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert url_for('profile.details', user_id=self.hidden_user.id) not in rv.data.decode('utf-8')

    def test_view_list_by_hidden(self):
        url = url_for('profile.all')
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        assert url_for('profile.details', user_id=self.hidden_user.id) in rv.data.decode('utf-8')

    def test_anon_view_profile(self):
        profile_url = url_for('profile.details', user_id=self.public_user.id)
        rv = self.client.get(profile_url)
        assert f'action="{profile_url}"' not in rv.data.decode('utf-8')

    def test_update_other_profile(self, user_factory):
        user = user_factory()
        profile_url = url_for('profile.details', user_id=self.public_user.id)
        self.login(user.email)
        data = {
            'nick': 'new nick',
        }
        rv = self.client.post(profile_url, data=data)
        assert rv.status_code == 403

    def test_update_by_anon(self):
        profile_url = url_for('profile.details', user_id=self.public_user.id)
        data = {
            'nick': 'new nick',
        }
        rv = self.client.post(profile_url, data=data)
        assert rv.status_code == 403

    def test_update_by_self(self):
        profile_url = url_for('profile.details', user_id=self.public_user.id)
        self.login(self.public_user.email)
        data = {
            'nick': 'Stephan',
            'email': self.public_user.email,
        }
        rv = self.client.post(profile_url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert BrewerProfile.get_by_email(self.public_user.email).nick == data['nick']

    def test_update_failure(self):
        profile_url = url_for('profile.details', user_id=self.public_user.id)
        self.login(self.public_user.email)
        data = {
            'nick': 'Stephan',
            'email': 'cowabungaitis',
        }
        rv = self.client.post(profile_url, data=data, follow_redirects=True)
        assert b'profile data has been updated' not in rv.data

    def test_view_hidden_by_public(self):
        profile_url = url_for('profile.details', user_id=self.hidden_user.id)
        self.login(self.public_user.email)
        rv = self.client.get(profile_url)
        assert rv.status_code == 404

    def test_owner_sees_delete_form(self):
        url = url_for('profile.delete', user_id=self.public_user.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert f'action="{url}"' in rv.data.decode('utf-8')

    def test_public_cant_access_delete_form(self):
        url = url_for('profile.delete', user_id=self.public_user.id)
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_delete_profile(self):
        user_id = self.public_user.id
        url = url_for('profile.delete', user_id=user_id)
        self.login(self.public_user.email)
        self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert BrewerProfile.query.get(user_id) is None


@pytest.mark.usefixtures('client_class')
class TestProfileBrews(BrewerProfileTests):

    def test_public(self):
        url = url_for('profile.brews', user_id=self.public_user.id)
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        assert self.pb_hidden_brew.name not in rv.data.decode('utf-8')

    def test_owner(self):
        url = url_for('profile.brews', user_id=self.public_user.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert self.pb_hidden_brew.name in rv.data.decode('utf-8')

    def test_hidden(self):
        url = url_for('profile.brews', user_id=self.hidden_user.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestProfileBreweries(BrewerProfileTests):

    def test_public(self):
        url = url_for('profile.breweries', user_id=self.public_user.id)
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        assert self.public_brewery.name in rv.data.decode('utf-8')

    def test_hidden(self):
        url = url_for('profile.breweries', user_id=self.hidden_user.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 404
