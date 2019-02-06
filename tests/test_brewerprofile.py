from flask import url_for
import pytest

from brewlog.models.users import BrewerProfile, CustomExportTemplate, CustomLabelTemplate

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestBrewerProfile(BrewlogTests):

    def test_login(self):
        user = BrewerProfile.get_by_email('user@example.com')
        # check redirect
        rv = self.client.get(url_for('auth.login', provider='local'), follow_redirects=False)
        assert 'localhost' in rv.headers.get('Location')
        # check target resource
        rv = self.login(self.client, user.email)
        assert 'You have been signed in as %s using local handler' % user.email in rv.data.decode('utf-8')

    def test_hidden_user(self):
        user = BrewerProfile.get_by_email('user3@example.com')
        rv = self.client.get(url_for('home.index'))
        assert '<a href="%s">%s</a>' % (user.absolute_url, user.name) in rv.data.decode('utf-8')

    def test_view_list_by_public(self):
        user = BrewerProfile.get_by_email('user@example.com')
        hidden_user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('profile.all')
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert hidden_user.absolute_url not in rv.data.decode('utf-8')

    def test_view_list_by_hidden(self):
        hidden_user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('profile.all')
        self.login(self.client, hidden_user.email)
        rv = self.client.get(url)
        hidden_user.absolute_url in rv.data.decode('utf-8')

    def test_anon_view_profile(self):
        user = BrewerProfile.get_by_email('user@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        rv = self.client.get(profile_url)
        assert 'action="%s"' % user.absolute_url not in rv.data.decode('utf-8')

    def test_update_other_profile(self):
        user1 = BrewerProfile.get_by_email('user1@example.com')
        user2 = BrewerProfile.get_by_email('user2@example.com')
        profile_url = url_for('profile.details', userid=user1.id)
        self.login(self.client, user2.email)
        data = {
            'nick': 'new nick',
        }
        rv = self.client.post(profile_url, data=data)
        assert rv.status_code == 403

    def test_update_by_anon(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        data = {
            'nick': 'new nick',
        }
        rv = self.client.post(profile_url, data=data)
        assert rv.status_code == 403

    def test_update_by_self(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        self.login(self.client, user.email)
        data = {
            'nick': 'Stephan',
            'email': user.email,
        }
        rv = self.client.post(profile_url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert BrewerProfile.get_by_email(user.email).nick == data['nick']

    def test_update_failure(self):
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=user.id)
        self.login(self.client, user.email)
        data = {
            'nick': 'Stephan',
            'email': 'cowabungaitis',
        }
        rv = self.client.post(profile_url, data=data, follow_redirects=True)
        assert b'profile data has been updated' not in rv.data

    def test_view_hidden_by_public(self):
        hidden = BrewerProfile.get_by_email('hidden1@example.com')
        user = BrewerProfile.get_by_email('user1@example.com')
        profile_url = url_for('profile.details', userid=hidden.id)
        self.login(self.client, user.email)
        rv = self.client.get(profile_url)
        assert rv.status_code == 404

    def test_owner_sees_delete_form(self):
        user = BrewerProfile.get_by_email('user@example.com')
        url = url_for('profile.delete', userid=user.id)
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_public_cant_access_delete_form(self):
        hidden = BrewerProfile.get_by_email('hidden1@example.com')
        user = BrewerProfile.get_by_email('user@example.com')
        url = url_for('profile.delete', userid=user.id)
        self.login(self.client, hidden.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_delete_profile(self):
        hidden = BrewerProfile.get_by_email('hidden1@example.com')
        user_id = hidden.id
        url = url_for('profile.delete', userid=user_id)
        self.login(self.client, hidden.email)
        self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert BrewerProfile.query.get(user_id) is None


@pytest.mark.usefixtures('client_class')
class TestProfileBrews(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.public_user = BrewerProfile.get_by_email('user1@example.com')
        self.hidden_user = BrewerProfile.get_by_email('hidden0@example.com')

    def test_public(self):
        url = url_for('profile.brews', userid=self.public_user.id)
        self.login(self.client, self.hidden_user.email)
        rv = self.client.get(url)
        assert b'hidden czech pilsener' not in rv.data

    def test_owner(self):
        url = url_for('profile.brews', userid=self.public_user.id)
        self.login(self.client, self.public_user.email)
        rv = self.client.get(url)
        assert b'hidden czech pilsener' in rv.data

    def test_hidden(self):
        url = url_for('profile.brews', userid=self.hidden_user.id)
        self.login(self.client, self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestProfileBreweries(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.public_user = BrewerProfile.get_by_email('user1@example.com')
        self.hidden_user = BrewerProfile.get_by_email('hidden0@example.com')

    def test_public(self):
        url = url_for('profile.breweries', userid=self.public_user.id)
        self.login(self.client, self.hidden_user.email)
        rv = self.client.get(url)
        assert b'brewery #1' in rv.data

    def test_hidden(self):
        url = url_for('profile.breweries', userid=self.hidden_user.id)
        self.login(self.client, self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestProfileExportTemplates(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.user = BrewerProfile.get_by_email('user1@example.com')
        self.template = self.user.custom_export_templates.first()

    def test_list_on_profile_page(self):
        url = url_for('profile.details', userid=self.user.id)
        self.login(self.client, self.user.email)
        rv = self.client.get(url)
        assert self.template.name in rv.data.decode('utf-8')

    def test_access_own(self):
        url = url_for('profile.export_template', userid=self.user.id, tid=self.template.id)
        self.login(self.client, self.user.email)
        rv = self.client.get(url)
        assert self.template.name in rv.data.decode('utf-8')

    def test_access_other(self):
        template = CustomExportTemplate.query.filter_by(name='custom #2').first()
        url = url_for('profile.export_template', userid=self.user.id, tid=template.id)
        self.login(self.client, self.user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_create(self):
        url = url_for('profile.export_template_add', userid=self.user.id)
        self.login(self.client, self.user.email)
        data = dict(name='new template', text='template')
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert CustomExportTemplate.query.filter_by(user=self.user).count() == 2
        assert data['name'] in rv.data.decode('utf-8')

    def test_edit(self):
        url = url_for('profile.export_template', userid=self.user.id, tid=self.template.id)
        self.login(self.client, self.user.email)
        data = dict(name='new custom template', text='new template text')
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert b'has been saved' in rv.data


@pytest.mark.usefixtures('client_class')
class TestLabelTemplates(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.user = BrewerProfile.get_by_email('user1@example.com')
        self.template = self.user.custom_label_templates.first()

    def test_list_in_profile_page(self):
        url = url_for('profile.details', userid=self.user.id)
        self.login(self.client, self.user.email)
        rv = self.client.get(url)
        assert self.template.name in rv.data.decode('utf-8')

    def test_access_own(self):
        url = url_for('profile.label_template', userid=self.user.id, tid=self.template.id)
        self.login(self.client, self.user.email)
        rv = self.client.get(url)
        assert self.template.name in rv.data.decode('utf-8')

    def test_access_other(self):
        template = CustomLabelTemplate.query.filter_by(name='custom #2').first()
        url = url_for('profile.label_template', userid=self.user.id, tid=template.id)
        self.login(self.client, self.user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_create(self):
        url = url_for('profile.label_template_add', userid=self.user.id)
        self.login(self.client, self.user.email)
        data = dict(name='new template', text='template')
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert CustomLabelTemplate.query.filter_by(user=self.user).count() == 2
        assert data['name'] in rv.data.decode('utf-8')

    def test_edit(self):
        url = url_for('profile.label_template', userid=self.user.id, tid=self.template.id)
        self.login(self.client, self.user.email)
        data = dict(name='new custom template', text='new template text')
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert b'has been saved' in rv.data
