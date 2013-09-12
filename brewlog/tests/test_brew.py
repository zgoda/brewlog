from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models import Brew


class BrewTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewTestCase, self).setUp()
        self.hidden_brew = Brew.query.filter_by(name='hidden amber ale').first()

    def test_regular_view_list(self):
        """
        Regular user (no matter logged in or not) sees only public brews in public breweries
        """
        url = url_for('brew-all')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertNotIn(self.hidden_brew.name, rv.data)