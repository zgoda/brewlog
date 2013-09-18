from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models import Brew, BrewerProfile, Brewery


class BrewTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()
        self.hidden_brew_indirect = Brew.query.filter_by(name='hidden amber ale').first()
        self.hidden_brew_direct = Brew.query.filter_by(name='hidden czech pilsener').first()
        self.hidden_user = BrewerProfile.get_by_email('hidden0@example.com')
        self.hidden_brewery = Brewery.query.filter_by(name='hidden brewery #1').first()
        self.list_url = url_for('brew-all')

    def test_regular_view_list(self):
        """
        Regular user (no matter logged in or not) sees only public brews in public breweries
        """
        with self.app.test_client() as client:
            rv = client.get(self.list_url)
            self.assertIn(self.brew.name, rv.data)
            self.assertNotIn(self.hidden_brew_indirect.name, rv.data)
            self.assertNotIn(self.hidden_brew_direct.name, rv.data)
            # delete button is not visible here
            self.assertNotIn(url_for('brew-delete', brew_id=self.brew.id), rv.data)

    def test_hidden_user_view_list(self):
        """
        Hidden user sees all public brews and from his own brewery
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.get(self.list_url)
            self.assertIn(self.brew.name, rv.data)
            self.assertIn(self.hidden_brew_indirect.name, rv.data)
            self.assertNotIn(self.hidden_brew_direct.name, rv.data)
            self.assertNotIn(url_for('brew-delete', brew_id=self.brew.id), rv.data)
            self.assertIn(url_for('brew-delete', brew_id=self.hidden_brew_indirect.id), rv.data)

    def test_hidden_brew_view_list(self):
        """
        Hidden brew in public brewery can be seen only by owner of the brewery
        """
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(self.list_url)
            self.assertIn(self.brew.name, rv.data)
            self.assertNotIn(self.hidden_brew_indirect.name, rv.data)
            self.assertIn(self.hidden_brew_direct.name, rv.data)
            self.assertIn(url_for('brew-delete', brew_id=self.brew.id), rv.data)
            self.assertIn(url_for('brew-delete', brew_id=self.hidden_brew_direct.id), rv.data)

    def test_view_public_details(self):
        """
        Only owner sees form for modify brew data
        """
        url = url_for('brew-details', brew_id=self.brew.id)
        with self.app.test_client() as client:
            # anon first
            rv = client.get(url)
            self.assertNotIn('<form', rv.data)
            # owner
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertIn('<form', rv.data)

    def test_view_hidden_details_indirect(self):
        url = url_for('brew-details', brew_id=self.hidden_brew_indirect.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)

    def test_view_hidden_details_direct(self):
        url = url_for('brew-details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)

    def test_view_hidden_details_by_owner_indirect(self):
        url = url_for('brew-details', brew_id=self.hidden_brew_indirect.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_indirect.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<form', rv.data)

    def test_view_hidden_details_by_owner_direct(self):
        url = url_for('brew-details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<form', rv.data)

    def test_update_by_owner(self):
        """
        Only brewery owner can update brew data
        """
        url = url_for('brew-details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            data = {
                'name': 'new name (still hidden)',
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(data['name'], rv.data)

    def test_update_by_public(self):
        """
        Non-owner can not update brew data
        """
        url = url_for('brew-details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            data = {
                'name': 'new name (still hidden)',
            }
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_delete_by_owner(self):
        """
        Delete brew by owner:
            * success
        """
        brew_id = self.hidden_brew_direct.id
        url = url_for('brew-delete', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIsNone(Brew.query.get(brew_id))

    def test_delete_by_other(self):
        brew_id = self.brew.id
        url = url_for('brew-delete', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.post(url, data={'delete_it': True})
            self.assertEqual(rv.status_code, 403)


class BrewExportTestCase(BrewlogTestCase):

    def test_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-export', brew_id=brew.id, flavour='ipboard')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertIn('<textarea', rv.data)

    def test_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-export', brew_id=brew.id, flavour='ipboard')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)

    def test_print_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-print', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)

    def test_print_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-print', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)

    def test_print_labels_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-print-labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)

    def test_print_labels_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-print-labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)