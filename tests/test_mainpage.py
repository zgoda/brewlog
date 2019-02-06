from flask import url_for
import pytest

from brewlog.models.users import BrewerProfile

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestMainPage(BrewlogTests):

    def test_anon(self):
        """
        case: what anonymous user sees on main site page:
            * box with recently registered users with public profiles
            * box with recently created public brews from public breweries
            * box with recently created breweries of users with public profile
            * box with recent tasting notes to public brews
            * link to main page
            * link to login page
        """
        main_url = url_for('home.index')
        rv = self.client.get(main_url)
        content = rv.data.decode('utf-8')
        # public profiles
        assert 'example user' in content
        assert 'hidden user' not in content
        # public breweries
        assert 'brewery #1' in content
        assert 'hidden brewery #1' not in content
        # public brews
        assert 'pale ale' in content
        assert 'hidden czech pilsener' not in content
        assert 'hidden amber ale' not in content
        # link to main page
        assert '>Brew Log</a>' in content
        # link to login page
        assert 'login page' in content

    def test_loggedin(self):
        main_url = url_for('home.index')
        # normal (public) profile user
        user = BrewerProfile.get_by_email('user@example.com')
        self.login(self.client, user.email)
        rv = self.client.get(main_url)
        content = rv.data.decode('utf-8')
        assert 'my profile</a>' in content
        assert 'pale ale' in content
        # hidden profile user
        user = BrewerProfile.get_by_email('hidden0@example.com')
        self.login(self.client, user.email)
        rv = self.client.get(main_url)
        assert 'hidden amber ale' in rv.data.decode('utf-8')
