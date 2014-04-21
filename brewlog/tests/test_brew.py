import datetime

from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models.brewing import Brew, Brewery
from brewlog.models.users import BrewerProfile, CustomLabelTemplate


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

    def test_add_by_anon(self):
        """
        Anonymous users can not add brews
        """
        url = url_for('brew-add')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertEqual(rv.status_code, 302)

    def test_add_form_visible_for_registered(self):
        """
        Registered users can access brew form.
        """
        url = url_for('brew-add')
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

    def test_add_by_registered(self):
        """
        Registered users can add brews.
        """
        url = url_for('brew-add')
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            data = {
                'name': 'new brew',
                'brewery': self.hidden_brew_direct.brewery.id,
                'carbonation_type': 'bottles with priming',
                'carbonation_level': 'normal',
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h3>%s</h3>' % data['name'], rv.data)
            self.assertIn(self.hidden_brew_direct.brewery.name, rv.data)

    def test_update_by_owner(self):
        """
        Only brewery owner can update brew data
        """
        url = url_for('brew-details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            data = {
                'name': 'new name (still hidden)',
                'brewery': self.hidden_brew_direct.brewery.id,
                'carbonation_type': 'bottles with priming',
                'carbonation_level': 'normal',
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h3>%s</h3>' % data['name'], rv.data)

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

    def test_owner_access_delete_form(self):
        brew_id = self.hidden_brew_direct.id
        url = url_for('brew-delete', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

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
            self.assertEqual(rv.status_code, 403)

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
            self.assertEqual(rv.status_code, 403)

    def test_print_labels_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-print-labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h3>#%s %s</h3>' % (brew.code, brew.name), rv.data)

    def test_print_custom_template(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('user1@example.com')
        template = CustomLabelTemplate.query.filter_by(user=user).first()
        url = url_for('brew-print-labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url, query_string={'template': template.id})
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h4>%s</h4>' % brew.name, rv.data)

    def test_print_labels_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew-print-labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)


class FermentationStepsTestCase(BrewlogTestCase):

    def setUp(self):
        super(FermentationStepsTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()
        self.brewery = self.brew.brewery
        self.user = self.brewery.brewer
        self.another_user = BrewerProfile.get_by_email('user2@example.com')

    def test_create_brew(self):
        brew = Brew(name='amber ale', brewery=self.brewery, date_brewed=datetime.datetime.utcnow(), code='3')
        # newly created brew has no fermentation steps
        self.assertEqual(brew.fermentation_steps.count(), 0)

    def test_add_fermentation_step_by_owner(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            data = {
                'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                'name': 'secondary',
            }
            rv = client.get(url_for('brew-details', brew_id=self.brew.id))
            self.assertNotIn(data['name'], rv.data)
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(data['name'], rv.data)

    def test_add_fermentation_step_by_public(self):
        url = url_for('brew-fermentationstep_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.another_user.email)
            data = {
                'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                'name': 'secondary',
            }
            rv = client.get(url_for('brew-details', brew_id=self.brew.id))
            self.assertNotIn(data['name'], rv.data)
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

    def test_add_fermentation_step_to_nonexisting_brew(self):
        brew_id = 666
        url = url_for('brew-fermentationstep_add', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            data = {
                'date': datetime.datetime.utcnow().strftime('%Y-%m-%d'),
                'name': 'primary',
            }
            rv = client.get(url_for('brew-details', brew_id=brew_id))
            self.assertEqual(rv.status_code, 404)
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 404)

    def test_delete_fermentation_step(self):
        fstep_name = self.brew.fermentation_steps.first().name
        fstep_id = self.brew.fermentation_steps.first().id
        url = url_for('brew-fermentationstep_delete', fstep_id=fstep_id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            data = {
                'delete_it': True
            }
            rv = self.client.post(url, data=data, follow_redirects=True)
            self.assertNotIn(fstep_name.encode('utf-8'), rv.data)

    def test_edit_fermentation_step_owner_sees_form(self):
        fstep = self.brew.fermentation_steps.first()
        url = url_for('brew-fermentation_step', fstep_id=fstep.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = self.client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(fstep.name, rv.data)

    def test_edit_fermentation_step_owner_can_modify(self):
        fstep = self.brew.fermentation_steps.first()
        url = url_for('brew-fermentation_step', fstep_id=fstep.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            data = {
                'name': 'primary (mod)',
                'date': fstep.date.strftime('%Y-%m-%d'),
                'og': fstep.og,
                'fg': fstep.fg,
            }
            rv = self.client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(data['name'].encode('utf-8'), rv.data)
