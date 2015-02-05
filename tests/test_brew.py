from flask import url_for

from brewlog.ext import db
from brewlog.utils.brewing import aa, ra
from tests import BrewlogTestCase
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
        self.list_url = url_for('brew.all')

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
            self.assertNotIn(url_for('brew.delete', brew_id=self.brew.id), rv.data)

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
            self.assertNotIn(url_for('brew.delete', brew_id=self.brew.id), rv.data)
            self.assertIn(url_for('brew.delete', brew_id=self.hidden_brew_indirect.id), rv.data)

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
            self.assertIn(url_for('brew.delete', brew_id=self.brew.id), rv.data)
            self.assertIn(url_for('brew.delete', brew_id=self.hidden_brew_direct.id), rv.data)

    def test_view_public_details(self):
        """
        Only owner sees form for modify brew data
        """
        url = url_for('brew.details', brew_id=self.brew.id)
        with self.app.test_client() as client:
            # anon first
            rv = client.get(url)
            self.assertNotIn('<form', rv.data)
            # owner
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertIn('<form', rv.data)

    def test_view_hidden_details_indirect(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_indirect.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)

    def test_view_hidden_details_direct(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)

    def test_view_hidden_details_by_owner_indirect(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_indirect.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_indirect.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<form', rv.data)

    def test_view_hidden_details_by_owner_direct(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<form', rv.data)

    def test_add_by_anon(self):
        """
        Anonymous users can not add brews
        """
        url = url_for('brew.add')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertEqual(rv.status_code, 302)

    def test_add_form_visible_for_registered(self):
        """
        Registered users can access brew form.
        """
        url = url_for('brew.add')
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

    def test_add_by_registered(self):
        """
        Registered users can add brews.
        """
        url = url_for('brew.add')
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            data = {
                'name': 'new brew',
                'brewery': self.hidden_brew_direct.brewery.id,
                'carbonation_type': 'bottles with priming',
                'carbonation_level': 'normal',
                'notes': 'new brew',
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h3>%s</h3>' % data['name'], rv.data)
            self.assertIn(self.hidden_brew_direct.brewery.name, rv.data)
            brew = Brew.query.filter_by(name=data['name']).first()
            self.assertEqual(brew.fermentation_steps.count(), 0)

    def test_update_by_owner(self):
        """
        Only brewery owner can update brew data
        """
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
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
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brewery.brewer.email)
            data = {
                'name': 'new name (still hidden)',
            }
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_owner_access_delete_form(self):
        brew_id = self.hidden_brew_direct.id
        url = url_for('brew.delete', brew_id=brew_id)
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
        url = url_for('brew.delete', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIsNone(Brew.query.get(brew_id))

    def test_delete_by_other(self):
        brew_id = self.brew.id
        url = url_for('brew.delete', brew_id=brew_id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.post(url, data={'delete_it': True})
            self.assertEqual(rv.status_code, 403)


class BrewListsTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewListsTestCase, self).setUp()
        self.brewer = BrewerProfile.get_by_email('user1@example.com')
        self.hidden_user = BrewerProfile.get_by_email('hidden1@example.com')

    def test_list_public_only_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=True)]
        hidden_brews = [x.id for x in Brew.query.join(Brewery).filter(
            Brewery.brewer==self.brewer, Brew.is_public==False
        ).all()]
        for x in hidden_brews:
            self.assertNotIn(x, brew_ids)

    def test_list_all_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=False)]
        self.assertEqual(len(brew_ids), 2)

    def test_list_public_in_hidden_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.hidden_user, public_only=True)]
        self.assertEqual(len(brew_ids), 0)

    def test_limit_public_only_in_public_brewery(self):
        limit = 0
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=True, limit=limit)]
        self.assertEqual(len(brew_ids), limit)

    def test_limit_all_in_public_brewery(self):
        limit = 1
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=False, limit=limit)]
        self.assertEqual(len(brew_ids), limit)


class BrewAttenuationTestCase(BrewlogTestCase):

    def setUp(self):
        super(BrewAttenuationTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()

    def test_attenuation_none_display(self):
        url = url_for('brew.details', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(self.brew.attenuation['apparent'], 0)
            self.assertEqual(self.brew.attenuation['real'], 0)
            self.assertNotIn('apparent', rv.data)

    def test_og_fg_set(self):
        fs = self.brew.fermentation_steps.first()
        fs.fg = 2.5
        db.session.add(fs)
        db.session.flush()
        attenuation = self.brew.attenuation
        self.assertEqual(attenuation['apparent'], aa(self.brew.og, self.brew.fg))
        self.assertEqual(attenuation['real'], ra(self.brew.og, self.brew.fg))


class BrewExportTestCase(BrewlogTestCase):

    def test_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.export', brew_id=brew.id, flavour='ipboard')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertIn('<textarea', rv.data)

    def test_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.export', brew_id=brew.id, flavour='ipboard')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_print_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.print', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)

    def test_print_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.print', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_print_labels_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h3>#%s %s</h3>' % (brew.code, brew.name), rv.data)

    def test_print_custom_template(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('user1@example.com')
        template = CustomLabelTemplate.query.filter_by(user=user).first()
        url = url_for('brew.labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url, query_string={'template': template.id})
            self.assertEqual(rv.status_code, 200)
            self.assertIn('<h4>%s</h4>' % brew.name, rv.data)

    def test_print_labels_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.labels', brew_id=brew.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)
