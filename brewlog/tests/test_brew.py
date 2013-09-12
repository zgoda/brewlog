from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models import Brew, BrewerProfile, Brewery


class BrewTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewTestCase, self).setUp()
        self.hidden_brew_indirect = Brew.query.filter_by(name='hidden amber ale').first()
        self.hidden_brew_direct = Brew.query.filter_by(name='hidden czech pilsener').first()
        self.hidden_user = BrewerProfile.get_by_email('hidden0@example.com')
        self.hidden_brewery = Brewery.query.filter_by(name='hidden brewery #1')
        self.list_url = url_for('brew-all')

    def test_regular_view_list(self):
        """
        Regular user (no matter logged in or not) sees only public brews in public breweries
        """
        with self.app.test_client() as client:
            rv = client.get(self.list_url)
            self.assertNotIn(self.hidden_brew_indirect.name, rv.data)
            self.assertNotIn(self.hidden_brew_direct.name, rv.data)

    def test_hidden_user_view_list(self):
        """
        Hidden user sees all public brews and from his own brewery
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.get(self.list_url)
            self.assertIn(self.hidden_brew_indirect.name, rv.data)
            self.assertNotIn(self.hidden_brew_direct.name, rv.data)

    def test_hidden_brew_view_list(self):
        """
        Hidden brew can be seen only by owner of the brewery
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(self.list_url)
            self.assertNotIn(self.hidden_brew_indirect.name, rv.data)
            self.assertIn(self.hidden_brew_direct.name, rv.data)