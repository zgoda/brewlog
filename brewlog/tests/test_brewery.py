from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models import Brewery


class BreweryTestCase(BrewlogTestCase):

    def test_anon_view(self):
        """
        View by anonymous user:
            * only basic information if public, 404 if hidden
        """
        public_brewery = Brewery.query.get(1)
        hidden_brewery = Brewery.query.get(3)
        with self.app.test_client() as client:
            rv = client.get(url_for('brewery-details', brewery_id=public_brewery.id))
            self.assertIn('>brewery #1</h', rv.data)
            rv = client.get(url_for('brewery-details', brewery_id=hidden_brewery.id))
            self.assertEqual(rv.status_code, 404)
