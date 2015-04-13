from flask import url_for

from tests import BrewlogTestCase
from brewlog.models.users import BrewerProfile, CustomExportTemplate, CustomLabelTemplate


class BrewerProfileTestCase(BrewlogTestCase):

    def test_login(self):
        user = BrewerProfile.get_by_email('user@example.com')
        target_url = url_for('home.index')
        with self.app.test_client() as client:
            # check redirect
            rv = client.get(url_for('auth.login', provider='local'), follow_redirects=False)
            self.assertRedirects(rv, target_url)
            # check target resource
            rv = self.login(client, user.email)
            self.assertIn('You have been signed in as %s using local handler' % user.email, rv.data)

    def test_hidden_user(self):
        user = BrewerProfile.get_by_email('user3@example.com')
        with self.app.test_client() as client:
            rv = client.get(url_for('home.index'))
            self.assertIn('<a href="%s">%s</a>' % (user.absolute_url, user.name), rv.data)

    def test_view_list_by_public(self):
        user = BrewerProfile.get_by_email('user@example.com')
        hidden_user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('profile.all')
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertNotIn(hidden_user.absolute_url, rv.data)

    def test_view_list_by_hidden(self):
        hidden_user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('profile.all')
        with self.app.test_client() as client:
            self.login(client, hidden_user.email)
            rv = client.get(url)
            self.assertIn(hidden_user.absolute_url, rv.data)

    def test_anon_view_profile(self):
        user = BrewerProfile.get_by_email('user@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        with self.app.test_client() as client:
            rv = client.get(profile_url)
            self.assertNotIn('<form', rv.data)

    def test_update_other_profile(self):
        user1 = BrewerProfile.get_by_email('user1@example.com')
        user2 = BrewerProfile.get_by_email('user2@example.com')
        profile_url = url_for('profile.details', userid=user1.id)
        with self.app.test_client() as client:
            self.login(client, user2.email)
            data = {
                'nick': 'new nick',
            }
            rv = client.post(profile_url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_update_by_anon(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        with self.app.test_client() as client:
            data = {
                'nick': 'new nick',
            }
            rv = client.post(profile_url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_update_by_self(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            data = {
                'nick': 'Stephan',
                'email': user.email,
            }
            rv = client.post(profile_url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(BrewerProfile.get_by_email(user.email).nick, data['nick'])

    def test_view_hidden_by_public(self):
        hidden = BrewerProfile.get_by_email('hidden1@example.com')
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=hidden.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(profile_url)
            self.assertEqual(rv.status_code, 404)

    def test_owner_sees_delete_form(self):
        user = BrewerProfile.get_by_email('user@example.com')
        url = url_for('profile.delete', userid=user.id)
        with self.app.test_client() as client:
            self.login(client, user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

    def test_public_cant_access_delete_form(self):
        hidden = BrewerProfile.get_by_email('hidden1@example.com')
        user = BrewerProfile.get_by_email('user@example.com')
        url = url_for('profile.delete', userid=user.id)
        with self.app.test_client() as client:
            self.login(client, hidden.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_delete_profile(self):
        hidden = BrewerProfile.get_by_email('hidden1@example.com')
        user_id = hidden.id
        url = url_for('profile.delete', userid=user_id)
        with self.app.test_client() as client:
            self.login(client, hidden.email)
            client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertIsNone(BrewerProfile.query.get(user_id))


class ProfileBrewsTestCase(BrewlogTestCase):

    def setUp(self):
        super(ProfileBrewsTestCase, self).setUp()
        self.public_user = BrewerProfile.get_by_email('user1@example.com')
        self.hidden_user = BrewerProfile.get_by_email('hidden0@example.com')

    def test_public(self):
        url = url_for('profile.brews', userid=self.public_user.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.get(url)
            self.assertNotIn('hidden czech pilsener', rv.data)

    def test_owner(self):
        url = url_for('profile.brews', userid=self.public_user.id)
        with self.app.test_client() as client:
            self.login(client, self.public_user.email)
            rv = client.get(url)
            self.assertIn('hidden czech pilsener', rv.data)

    def test_hidden(self):
        url = url_for('profile.brews', userid=self.hidden_user.id)
        with self.app.test_client() as client:
            self.login(client, self.public_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)


class ProfileBreweriesTestCase(BrewlogTestCase):

    def setUp(self):
        super(ProfileBreweriesTestCase, self).setUp()
        self.public_user = BrewerProfile.get_by_email('user1@example.com')
        self.hidden_user = BrewerProfile.get_by_email('hidden0@example.com')

    def test_public(self):
        url = url_for('profile.breweries', userid=self.public_user.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_user.email)
            rv = client.get(url)
            self.assertIn('brewery #1', rv.data)

    def test_hidden(self):
        url = url_for('profile.breweries', userid=self.hidden_user.id)
        with self.app.test_client() as client:
            self.login(client, self.public_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 404)


class ProfileExportTemplatesTestCase(BrewlogTestCase):

    def setUp(self):
        super(ProfileExportTemplatesTestCase, self).setUp()
        self.user = BrewerProfile.get_by_email('user1@example.com')
        self.template = self.user.custom_export_templates.first()

    def test_list_in_profile_page(self):
        url = url_for('profile.details', userid=self.user.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = client.get(url)
            self.assertIn(self.template.name, rv.data)

    def test_access_own(self):
        url = url_for('profile.export_template', userid=self.user.id, tid=self.template.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = client.get(url)
            self.assertIn(self.template.name, rv.data)

    def test_access_other(self):
        template = CustomExportTemplate.query.filter_by(name='custom #2').first()
        url = url_for('profile.export_template', userid=self.user.id, tid=template.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_create(self):
        url = url_for('profile.export_template_add', userid=self.user.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            data = dict(name='new template', text='template')
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(CustomExportTemplate.query.filter_by(user=self.user).count(), 2)
            self.assertIn(data['name'], rv.data)


class LabelTemplatesTestCase(BrewlogTestCase):

    def setUp(self):
        super(LabelTemplatesTestCase, self).setUp()
        self.user = BrewerProfile.get_by_email('user1@example.com')
        self.template = self.user.custom_label_templates.first()

    def test_list_in_profile_page(self):
        url = url_for('profile.details', userid=self.user.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = client.get(url)
            self.assertIn(self.template.name, rv.data)

    def test_access_own(self):
        url = url_for('profile.label_template', userid=self.user.id, tid=self.template.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = client.get(url)
            self.assertIn(self.template.name, rv.data)

    def test_access_other(self):
        template = CustomLabelTemplate.query.filter_by(name='custom #2').first()
        url = url_for('profile.label_template', userid=self.user.id, tid=template.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_create(self):
        url = url_for('profile.label_template_add', userid=self.user.id)
        with self.app.test_client() as client:
            self.login(client, self.user.email)
            data = dict(name='new template', text='template')
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(CustomLabelTemplate.query.filter_by(user=self.user).count(), 2)
            self.assertIn(data['name'], rv.data)
