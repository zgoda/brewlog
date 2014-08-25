import urllib
import datetime

from flask import url_for

from tests import BrewlogTestCase
from brewlog.models.brewing import Brewery, Brew


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
            url = url_for('brewery.all')
            self.login(client, self.public_brewery.brewer.email)
            rv = client.get(url)
            self.assertNotIn(self.hidden_brewery.name, rv.data)
            self.assertIn(url_for('brewery.delete', brewery_id=self.public_brewery.id), rv.data)

    def test_owner_view_list(self):
        """
        Owner of hidden brewery can see it on the list
        """
        with self.app.test_client() as client:
            url = url_for('brewery.all')
            self.login(client, self.hidden_brewery.brewer.email)
            rv = client.get(url)
            self.assertIn(self.hidden_brewery.name, rv.data)
            self.assertIn(url_for('brewery.delete', brewery_id=self.hidden_brewery.id), rv.data)

    def test_anon_view_list(self):
        url = url_for('brewery.all')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertNotIn(self.hidden_brewery.name, rv.data)
            self.assertIn(self.public_brewery.name, rv.data)
            self.assertNotIn(url_for('brewery.delete', brewery_id=self.public_brewery.id), rv.data)

    def test_nonowner_view(self):
        """
        View by ordinary user:
            * only basic information if public
            * 404 if hidden
        """
        with self.app.test_client() as client:
            rv = client.get(url_for('brewery.details', brewery_id=self.public_brewery.id))
            self.assertIn(self.public_brewery.name, rv.data)
            self.assertNotIn('<form', rv.data)
            rv = client.get(url_for('brewery.details', brewery_id=self.hidden_brewery.id))
            self.assertEqual(rv.status_code, 404)

    def test_owner_view(self):
        """
        View by logged in user, owner of one of the breweries:
            * only basic information in non-owned
            * form in owned, even if hidden
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            rv = client.get(url_for('brewery.details', brewery_id=self.public_brewery.id))
            self.assertIn(self.public_brewery.name, rv.data)
            self.assertNotIn('<form', rv.data)
            rv = client.get(url_for('brewery.details', brewery_id=self.hidden_brewery.id))
            self.assertIn('<form', rv.data)

    def test_nonowner_change(self):
        """
        Change data by non owner:
            * 403
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            url = url_for('brewery.details', brewery_id=self.public_brewery.id)
            rv = client.post(url, data={'name': 'new name'})
            self.assertEqual(rv.status_code, 403)

    def test_owner_change(self):
        """
        Change data by owner:
            * success
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            url = url_for('brewery.details', brewery_id=self.hidden_brewery.id)
            new_name = 'new name'
            rv = client.post(url, data={'name': new_name}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(new_name, rv.data)
            brewery = Brewery.query.get(self.hidden_brewery.id)
            self.assertEqual(brewery.name, new_name)

    def test_owner_access_delete_form(self):
        url = url_for('brewery.delete', brewery_id=self.hidden_brewery.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            rv = client.get(url)
            self.assertIn('action="%s"' % url, rv.data)

    def test_owner_delete(self):
        """
        Delete brewery by owner:
            * success
        """
        brewery_id = self.hidden_brewery.id
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            url = url_for('brewery.delete', brewery_id=self.hidden_brewery.id)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIsNone(Brewery.query.get(brewery_id))

    def test_nonowner_delete(self):
        """
        Delete brewery by non owner:
            * 403
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            url = url_for('brewery.delete', brewery_id=self.public_brewery.id)
            rv = client.post(url, data={'delete_it': True})
            self.assertEqual(rv.status_code, 403)

    def test_add_form_visible_for_registered(self):
        url = url_for('brewery.add')
        with self.app.test_client() as client:
            self.login(client, self.public_brewery.brewer.email)
            rv = client.get(url)
            self.assertIn('action="%s"' % url, rv.data)

    def test_create_logged_in_user(self):
        with self.app.test_client() as client:
            self.login(client, self.public_brewery.brewer.email)
            data = {
                'name': 'new brewery',
                'description': 'new brewery in town',
                'established_date': datetime.datetime.utcnow().strftime('%Y-%m-%d')
            }
            url = url_for('brewery.add')
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertIn(data['name'], rv.data)

    def test_create_anon(self):
        with self.app.test_client() as client:
            data = {
                'name': 'new brewery',
            }
            url = url_for('brewery.add')
            redirect_url = url_for('auth-select-provider') + '?%s' % urllib.urlencode({'next': url})
            rv = client.post(url, data=data, follow_redirects=False)
            self.assertRedirects(rv, redirect_url)


class BreweryBrewsTestCase(BrewlogTestCase):

    """
    List of brews from single brewery:
        * owner sees everything
        * others see only public brews
        * if brewery is hidden others get 404
    """

    def setUp(self):
        super(BreweryBrewsTestCase, self).setUp()
        self.public_brewery = Brewery.query.filter_by(name='brewery #1').first()
        self.hidden_brewery = Brewery.query.filter_by(name='hidden brewery #1').first()

    def test_owner_view(self):
        url = url_for('brewery.brews', brewery_id=self.public_brewery.id)
        hidden_brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        with self.app.test_client() as client:
            self.login(client, self.public_brewery.brewer.email)
            rv = client.get(url)
            self.assertIn(hidden_brew.name, rv.data)

    def test_public_view(self):
        url = url_for('brewery.brews', brewery_id=self.public_brewery.id)
        hidden_brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            rv = client.get(url)
            self.assertNotIn(hidden_brew.name, rv.data)

    def test_hidden_view_by_public(self):
        url = url_for('brewery.brews', brewery_id=self.hidden_brewery.id)
        with self.app.test_client() as client:
            self.login(client, self.public_brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)
