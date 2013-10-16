from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models.users import BrewerProfile


class MainPageTestCase(BrewlogTestCase):

    def setUp(self):
        super(MainPageTestCase, self).setUp()
        self.main_url = url_for('main')

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
        with self.app.test_client() as client:
            rv = client.get(self.main_url)
            # public profiles
            self.assertIn('example user', rv.data)
            self.assertNotIn('hidden user', rv.data)
            # public breweries
            self.assertIn('brewery #1', rv.data)
            self.assertNotIn('hidden brewery #1', rv.data)
            # public brews
            self.assertIn('pale ale', rv.data)
            self.assertNotIn('hidden czech pilsener', rv.data)
            self.assertNotIn('hidden amber ale', rv.data)
            # link to main page
            self.assertIn('>Brew Log</a>', rv.data)
            # link to login page
            self.assertIn('login page', rv.data)

    def test_loggedin(self):
        """
        case: what logged in user sees on main site page:
            * box with recently registered users with public profiles and self if hidden
            * box with recently created public brews from public breweries and own if hidden
            * box with recently created breweries of users with public profile and own if hidden
            * link to main page
            * link to profile page
        """
        # normal (public) profile user
        user = BrewerProfile.get_by_email('user@example.com')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(self.main_url)
            self.assertIn('>my profile</a>', rv.data)
            # public profiles only
            self.assertIn('example user', rv.data)
            self.assertNotIn('hidden user', rv.data)
            # public breweries only
            self.assertIn('brewery #1', rv.data)
            self.assertNotIn('hidden brewery #1', rv.data)
            # public brews only
            self.assertIn('pale ale', rv.data)
            self.assertNotIn('hidden czech pilsener', rv.data)
            self.assertNotIn('hidden amber ale', rv.data)
        # hidden profile user
        user = BrewerProfile.get_by_email('hidden0@example.com')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(self.main_url)
            # public profiles and own
            self.assertIn('example user', rv.data)
            self.assertIn('hidden user', rv.data)
            # public breweries and own
            self.assertIn('brewery #1', rv.data)
            self.assertIn('hidden brewery #1', rv.data)
            # public brews and own
            self.assertIn('pale ale', rv.data)
            self.assertNotIn('hidden czech pilsener', rv.data)
            self.assertIn('hidden amber ale', rv.data)
