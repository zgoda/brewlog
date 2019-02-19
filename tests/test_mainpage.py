from flask import url_for
import pytest

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestMainPageAnonUser(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory):
        self.url = url_for('home.index')
        self.regular_brewery_name = 'regular brewery no 1'
        self.hidden_brewery_name = 'hidden brewery no 1'
        self.regular_brew_name = 'regular brew no 1'
        self.hidden_brew_name = 'hidden brew no 1'
        self.hidden_user = user_factory(is_public=False)
        self.regular_user = user_factory()

    def test_common_elements(self):
        rv = self.client.get(self.url)
        assert b'>Brew Log</a>' in rv.data
        assert b'login page' in rv.data

    def test_profile_visibility(self):
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.regular_user.full_name in page
        assert self.hidden_user.full_name not in page

    def test_brewery_visibility_regular_user(self, brewery_factory):
        brewery = brewery_factory(brewer=self.regular_user, name=self.regular_brewery_name)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.regular_user.full_name in page
        assert brewery.name in page

    def test_brewery_visibility_hidden_user(self, brewery_factory):
        brewery = brewery_factory(brewer=self.hidden_user, name=self.hidden_brewery_name)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.hidden_user.full_name not in page
        assert brewery.name not in page

    def test_brew_visibility_regular_brew_regular_user(self, brew_factory, brewery_factory):
        brewery = brewery_factory(brewer=self.regular_user, name=self.regular_brewery_name)
        brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.regular_user.full_name in page
        assert brewery.name in page
        assert brew.name in page

    def test_brew_visibility_regular_brew_hidden_user(self, brew_factory, brewery_factory):
        brewery = brewery_factory(brewer=self.hidden_user, name=self.regular_brewery_name)
        brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.hidden_user.full_name not in page
        assert brewery.name not in page
        assert brew.name not in page

    def test_brew_visibility_hidden_brew_hidden_user(self, brew_factory, brewery_factory):
        brewery = brewery_factory(brewer=self.hidden_user, name=self.regular_brewery_name)
        brew = brew_factory(brewery=brewery, name=self.regular_brew_name, is_public=False)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.hidden_user.full_name not in page
        assert brewery.name not in page
        assert brew.name not in page

    def test_brew_visibility_hidden_brew_regular_user(self, brew_factory, brewery_factory):
        brewery = brewery_factory(brewer=self.regular_user, name=self.regular_brewery_name)
        brew = brew_factory(brewery=brewery, name=self.regular_brew_name, is_public=False)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert self.regular_user.full_name in page
        assert brewery.name in page
        assert brew.name not in page


@pytest.mark.usefixtures('client_class')
class TestMainPageLoggedInRegularUser(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory):
        self.url = url_for('home.index')
        self.regular_brewery_name = 'regular brewery no 1'
        self.hidden_brewery_name = 'hidden brewery no 1'
        self.regular_brew_name = 'regular brew no 1'
        self.hidden_brew_name = 'hidden brew no 1'
        self.user = user_factory()

    def test_common_elements(self):
        self.login(self.client, self.user.email)
        rv = self.client.get(self.url)
        assert b'>Brew Log</a>' in rv.data
        assert b'my profile' in rv.data
        assert b'login page' not in rv.data

    def test_dashboard_brews(self, brew_factory, brewery_factory):
        self.login(self.client, self.user.email)
        brewery = brewery_factory(brewer=self.user, name=self.regular_brewery_name)
        regular_brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        hidden_brew = brew_factory(brewery=brewery, name=self.hidden_brew_name)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert regular_brew.name in page
        assert hidden_brew.name in page


@pytest.mark.usefixtures('client_class')
class TestMainPageLoggedInHiddenUser(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory):
        self.url = url_for('home.index')
        self.brewery_name = 'regular brewery no 1'
        self.regular_brew_name = 'regular brew no 1'
        self.hidden_brew_name = 'hidden brew no 1'
        self.user = user_factory(is_public=False)

    def test_common_elements(self):
        self.login(self.client, self.user.email)
        rv = self.client.get(self.url)
        assert b'>Brew Log</a>' in rv.data
        assert b'my profile' in rv.data
        assert b'login page' not in rv.data

    def test_dashboard_brews(self, brew_factory, brewery_factory):
        self.login(self.client, self.user.email)
        brewery = brewery_factory(brewer=self.user, name=self.brewery_name)
        regular_brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        hidden_brew = brew_factory(brewery=brewery, name=self.hidden_brew_name)
        rv = self.client.get(self.url)
        page = rv.data.decode('utf-8')
        assert regular_brew.name in page
        assert hidden_brew.name in page
