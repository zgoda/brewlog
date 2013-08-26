from brewlog.tests import BrewlogTestCase


class MainPageTestCase(BrewlogTestCase):

    def test_anon(self):
        """
        case: what anonymous user sees on main site page:
            * box with recently registered users with public profiles
            * box with recently created public brews from public breweries
            * box with recently created breweries of users with public profile
            * link to main page
            * link to login page
        """
        with self.app.test_client() as client:
            rv = client.get('/')
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
            * box with recently registered users with public profiles and self
            * box with recently created public brews from public breweries and own
            * box with recently created breweries of users with public profile and own
            * link to main page
            * link to profile page
        """
        pass
