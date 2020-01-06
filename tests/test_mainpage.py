import os

import pytest
from flask import url_for

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestMainPageAnonUser(BrewlogTests):

    TEMPLATES_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'src/brewlog/templates',
    )

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('home.index')
        self.regular_brewery_name = 'regular brewery no 1'
        self.hidden_brewery_name = 'hidden brewery no 1'
        self.regular_brew_name = 'regular brew no 1'
        self.hidden_brew_name = 'hidden brew no 1'

    def test_common_elements(self):
        rv = self.client.get(self.url)
        assert '>Brew Log</a>' in rv.text
        assert 'login page' in rv.text

    def test_profile_visibility(self, user_factory):
        public_user = user_factory(is_public=True)
        hidden_user = user_factory(is_public=False)
        rv = self.client.get(self.url)
        assert public_user.full_name in rv.text
        assert hidden_user.full_name not in rv.text

    def test_brewery_visibility_regular_user(self, user_factory, brewery_factory):
        public_user = user_factory(is_public=True)
        brewery = brewery_factory(
            brewer=public_user, name=self.regular_brewery_name
        )
        rv = self.client.get(self.url)
        assert public_user.full_name in rv.text
        assert brewery.name in rv.text

    def test_brewery_visibility_hidden_user(self, user_factory, brewery_factory):
        user = user_factory(is_public=False)
        brewery = brewery_factory(
            brewer=user, name=self.hidden_brewery_name
        )
        rv = self.client.get(self.url)
        assert user.full_name not in rv.text
        assert brewery.name not in rv.text

    def test_brew_visibility_regular_brew_regular_user(
                self, brew_factory, brewery_factory, user_factory,
            ):
        user = user_factory(is_public=True)
        brewery = brewery_factory(
            brewer=user, name=self.regular_brewery_name
        )
        brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        rv = self.client.get(self.url)
        assert user.full_name in rv.text
        assert brewery.name in rv.text
        assert brew.name in rv.text

    def test_brew_visibility_regular_brew_hidden_user(
                self, brew_factory, brewery_factory, user_factory,
            ):
        user = user_factory(is_public=False)
        brewery = brewery_factory(
            brewer=user, name=self.regular_brewery_name
        )
        brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        rv = self.client.get(self.url)
        assert user.full_name not in rv.text
        assert brewery.name not in rv.text
        assert brew.name not in rv.text

    def test_brew_visibility_hidden_brew_hidden_user(
                self, brew_factory, brewery_factory, user_factory,
            ):
        user = user_factory(is_public=False)
        brewery = brewery_factory(
            brewer=user, name=self.regular_brewery_name
        )
        brew = brew_factory(
            brewery=brewery, name=self.regular_brew_name, is_public=False
        )
        rv = self.client.get(self.url)
        assert user.full_name not in rv.text
        assert brewery.name not in rv.text
        assert brew.name not in rv.text

    def test_brew_visibility_hidden_brew_regular_user(
                self, brew_factory, brewery_factory, user_factory,
            ):
        user = user_factory(is_public=True)
        brewery = brewery_factory(
            brewer=user, name=self.regular_brewery_name
        )
        brew = brew_factory(
            brewery=brewery, name=self.regular_brew_name, is_public=False
        )
        rv = self.client.get(self.url)
        assert user.full_name in rv.text
        assert brewery.name in rv.text
        assert brew.name not in rv.text

    @pytest.mark.options(ANNOUNCEMENT_FILE='/tmp/dummy/announcement.md')
    def test_announcement_present(self, fs):
        file_name = '/tmp/dummy/announcement.md'
        fs.create_file(file_name, contents='This **very important** announcement.')
        fs.add_real_directory(self.TEMPLATES_DIR)
        rv = self.client.get(self.url)
        assert '<strong>very important</strong>' in rv.text


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
        self.login(self.user.email)
        rv = self.client.get(self.url)
        assert '>Brew Log</a>' in rv.text
        assert 'my profile' in rv.text
        assert 'login page' not in rv.text

    def test_dashboard_brews(self, brew_factory, brewery_factory):
        self.login(self.user.email)
        brewery = brewery_factory(brewer=self.user, name=self.regular_brewery_name)
        regular_brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        hidden_brew = brew_factory(brewery=brewery, name=self.hidden_brew_name)
        rv = self.client.get(self.url)
        assert regular_brew.name in rv.text
        assert hidden_brew.name in rv.text


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
        self.login(self.user.email)
        rv = self.client.get(self.url)
        assert '>Brew Log</a>' in rv.text
        assert 'my profile' in rv.text
        assert 'login page' not in rv.text

    def test_dashboard_brews(self, brew_factory, brewery_factory):
        self.login(self.user.email)
        brewery = brewery_factory(brewer=self.user, name=self.brewery_name)
        regular_brew = brew_factory(brewery=brewery, name=self.regular_brew_name)
        hidden_brew = brew_factory(brewery=brewery, name=self.hidden_brew_name)
        rv = self.client.get(self.url)
        assert regular_brew.name in rv.text
        assert hidden_brew.name in rv.text
