from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models import Brewery


class BreweryTestCase(BrewlogTestCase):

    def setUp(self):
        super(BreweryTestCase, self).setUp()
        self.public_brewery = Brewery.query.filter_by(name='brewery #1').first()
        self.hidden_brewery = Brewery.query.filter_by(name='hidden brewery #1').first()

    def test_nonowner_view_list(self):
        """
        Hidden breweries can not be seen by non owner
        """
        with self.app.test_client() as client:
            url = url_for('brewery-all')
            self.login(client, self.public_brewery.brewer.email)
            rv = client.get(url)
            self.assertNotIn(self.hidden_brewery.name, rv.data)

    def test_nonowner_view(self):
        """
        View by ordinary user:
            * only basic information if public
            * 404 if hidden
        """
        with self.app.test_client() as client:
            rv = client.get(url_for('brewery-details', brewery_id=self.public_brewery.id))
            self.assertIn(self.public_brewery.name, rv.data)
            self.assertNotIn('<form', rv.data)
            rv = client.get(url_for('brewery-details', brewery_id=self.hidden_brewery.id))
            self.assertEqual(rv.status_code, 404)

    def test_owner_view(self):
        """
        View by logged in user, owner of one of the breweries:
            * only basic information in non-owned
            * form in owned, even if hidden
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            rv = client.get(url_for('brewery-details', brewery_id=self.public_brewery.id))
            self.assertIn(self.public_brewery.name, rv.data)
            self.assertNotIn('<form', rv.data)
            rv = client.get(url_for('brewery-details', brewery_id=self.hidden_brewery.id))
            self.assertIn('<form', rv.data)

    def test_nonowner_change(self):
        """
        Change data by non owner:
            * 403
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            url = url_for('brewery-details', brewery_id=self.public_brewery.id)
            rv = client.post(url, data={'name': 'new name'})
            self.assertEqual(rv.status_code, 403)

    def test_owner_change(self):
        """
        Change data by owner:
            * success
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            url = url_for('brewery-details', brewery_id=self.hidden_brewery.id)
            new_name = 'new name'
            rv = client.post(url, data={'name': new_name}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(new_name, rv.data)
            brewery = Brewery.query.get(self.hidden_brewery.id)
            self.assertEqual(brewery.name, new_name)
