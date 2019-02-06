from flask import url_for
import pytest

from brewlog.ext import db
from brewlog.models.brewing import Brew, Brewery
from brewlog.models.users import BrewerProfile, CustomLabelTemplate
from brewlog.utils.brewing import apparent_attenuation, real_attenuation

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestBrew(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
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
        rv = self.client.get(self.list_url)
        content = rv.data.decode('utf-8')
        assert self.brew.name in content
        assert self.hidden_brew_indirect.name not in content
        assert self.hidden_brew_direct.name not in content
        # delete button is not visible here
        assert url_for('brew.delete', brew_id=self.brew.id) not in content

    def test_hidden_user_view_list(self):
        """
        Hidden user sees all public brews and from his own brewery
        """
        self.login(self.client, self.hidden_user.email)
        rv = self.client.get(self.list_url)
        content = rv.data.decode('utf-8')
        assert self.brew.name in content
        assert self.hidden_brew_indirect.name in content
        assert self.hidden_brew_direct.name not in content
        assert url_for('brew.delete', brew_id=self.brew.id) not in content
        assert url_for('brew.delete', brew_id=self.hidden_brew_indirect.id) in content

    def test_hidden_brew_view_list(self):
        """
        Hidden brew in public brewery can be seen only by owner of the brewery
        """
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        rv = self.client.get(self.list_url)
        content = rv.data.decode('utf-8')
        assert self.brew.name in content
        assert self.hidden_brew_indirect.name not in content
        assert self.hidden_brew_direct.name in content
        assert url_for('brew.delete', brew_id=self.brew.id) in content
        assert url_for('brew.delete', brew_id=self.hidden_brew_direct.id) in content

    def test_view_public_details(self):
        """
        Only owner sees form for modify brew data
        """
        url = url_for('brew.details', brew_id=self.brew.id)
        search_text = 'action="%s"' % self.brew.absolute_url
        # anon first
        rv = self.client.get(url)
        assert search_text not in rv.data.decode('utf-8')
        # owner
        self.login(self.client, self.brew.brewery.brewer.email)
        rv = self.client.get(url)
        assert search_text in rv.data.decode('utf-8')

    def test_view_hidden_details_indirect(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_indirect.id)
        self.login(self.client, self.brew.brewery.brewer.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    def test_view_hidden_details_direct(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        self.login(self.client, self.hidden_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    def test_view_hidden_details_by_owner_indirect(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_indirect.id)
        self.login(self.client, self.hidden_brew_indirect.brewery.brewer.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert '<form' in rv.data.decode('utf-8')

    def test_view_hidden_details_by_owner_direct(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert '<form' in rv.data.decode('utf-8')

    def test_add_by_anon(self):
        """
        Anonymous users can not add brews
        """
        url = url_for('brew.add')
        rv = self.client.get(url)
        assert rv.status_code == 302

    def test_add_form_visible_for_registered(self):
        """
        Registered users can access brew form.
        """
        url = url_for('brew.add')
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_add_by_registered(self):
        """
        Registered users can add brews.
        """
        url = url_for('brew.add')
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        data = {
            'name': 'new brew',
            'brewery': self.hidden_brew_direct.brewery.id,
            'carbonation_type': 'bottles with priming',
            'carbonation_level': 'normal',
            'notes': 'new brew',
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        content = rv.data.decode('utf-8')
        assert '<h3>%s</h3>' % data['name'] in content
        assert self.hidden_brew_direct.brewery.name in content
        brew = Brew.query.filter_by(name=data['name']).first()
        assert brew.fermentation_steps.count() == 0

    def test_update_by_owner(self):
        """
        Only brewery owner can update brew data
        """
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        data = {
            'name': 'new name (still hidden)',
            'brewery': self.hidden_brew_direct.brewery.id,
            'carbonation_type': 'bottles with priming',
            'carbonation_level': 'normal',
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert '<h3>%s</h3>' % data['name'] in rv.data.decode('utf-8')

    def test_update_by_public(self):
        """
        Non-owner can not update brew data
        """
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        self.login(self.client, self.hidden_brewery.brewer.email)
        data = {
            'name': 'new name (still hidden)',
        }
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    def test_owner_access_delete_form(self):
        brew_id = self.hidden_brew_direct.id
        url = url_for('brew.delete', brew_id=brew_id)
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_delete_by_owner(self):
        """
        Delete brew by owner:
            * success
        """
        brew_id = self.hidden_brew_direct.id
        url = url_for('brew.delete', brew_id=brew_id)
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 200
        assert Brew.query.get(brew_id) is None

    def test_delete_by_other(self):
        brew_id = self.brew.id
        url = url_for('brew.delete', brew_id=brew_id)
        self.login(self.client, self.hidden_user.email)
        rv = self.client.post(url, data={'delete_it': True})
        assert rv.status_code == 403

    def test_next_own_brews(self):
        brew_id = self.brew.id
        url = url_for('brew.details', brew_id=brew_id)
        self.login(self.client, self.brew.brewery.brewer.email)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        next_url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        assert '<a href="%s">next</a>' % next_url in content
        assert '>previous</a>' not in content

    def test_previous_own_brews(self):
        url = url_for('brew.details', brew_id=self.hidden_brew_direct.id)
        self.login(self.client, self.hidden_brew_direct.brewery.brewer.email)
        rv = self.client.get(url)
        prev_url = url_for('brew.details', brew_id=self.brew.id)
        assert '<a href="%s">previous</a>' % prev_url in rv.data.decode('utf-8')

    def test_previous_anon(self):
        """non-public brews should not be accessible in prev/next navigation for anonymous user"""
        brew = Brew.query.get(6)
        url = url_for('brew.details', brew_id=brew.id)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert '<a href="%s">previous</a>' % url_for('brew.details', brew_id=4) in content
        assert url_for('brew.details', brew_id=5) not in content

    def test_next_anon(self):
        brew = Brew.query.get(4)
        url = url_for('brew.details', brew_id=brew.id)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert '<a href="%s">next</a>' % url_for('brew.details', brew_id=6) in content
        assert url_for('brew.details', brew_id=5) not in content


@pytest.mark.usefixtures('client_class')
class TestBrewLists(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.brewer = BrewerProfile.get_by_email('user1@example.com')
        self.hidden_user = BrewerProfile.get_by_email('hidden1@example.com')

    def test_list_public_only_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=True)]
        hidden_brews = [x.id for x in Brew.query.join(Brewery).filter(
            Brewery.brewer == self.brewer, Brew.is_public.is_(False)
        ).all()]
        for x in hidden_brews:
            assert x not in brew_ids

    def test_list_all_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=False)]
        assert len(brew_ids) == 5

    def test_list_public_in_hidden_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.hidden_user, public_only=True)]
        assert len(brew_ids) == 0

    def test_limit_public_only_in_public_brewery(self):
        limit = 0
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=True, limit=limit)]
        assert len(brew_ids) == limit

    def test_limit_all_in_public_brewery(self):
        limit = 1
        brew_ids = [x.id for x in Brew.get_latest_for(self.brewer, public_only=False, limit=limit)]
        assert len(brew_ids) == limit


@pytest.mark.usefixtures('client_class')
class TestBrewAttenuation(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.brew = Brew.query.filter_by(name='pale ale').first()

    def test_attenuation_none_display(self):
        url = url_for('brew.details', brew_id=self.brew.id)
        self.login(self.client, self.brew.brewery.brewer.email)
        rv = self.client.get(url)
        assert self.brew.attenuation['apparent'] == 0
        assert self.brew.attenuation['real'] == 0
        assert b'apparent' not in rv.data

    def test_og_fg_set(self):
        fs = self.brew.fermentation_steps.first()
        fs.fg = 2.5
        db.session.add(fs)
        db.session.flush()
        attenuation = self.brew.attenuation
        assert attenuation['apparent'] == apparent_attenuation(self.brew.og, self.brew.fg)
        assert attenuation['real'] == real_attenuation(self.brew.og, self.brew.fg)


@pytest.mark.usefixtures('client_class')
class TestBrewExport(BrewlogTests):

    def test_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.export', brew_id=brew.id, flavour='ipboard')
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert b'<textarea' in rv.data

    def test_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.export', brew_id=brew.id, flavour='ipboard')
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_print_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.print', brew_id=brew.id)
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200

    def test_print_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.print', brew_id=brew.id)
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_print_labels_public(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.labels', brew_id=brew.id)
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert '<h3>#%s %s</h3>' % (brew.code, brew.name) in rv.data.decode('utf-8')

    def test_print_custom_template(self):
        brew = Brew.query.filter_by(name='pale ale').first()
        user = BrewerProfile.get_by_email('user1@example.com')
        template = CustomLabelTemplate.query.filter_by(user=user).first()
        url = url_for('brew.labels', brew_id=brew.id)
        self.login(self.client, user.email)
        rv = self.client.get(url, query_string={'template': template.id})
        assert rv.status_code == 200
        assert '<h4>%s</h4>' % brew.name in rv.data.decode('utf-8')

    def test_print_labels_hidden(self):
        brew = Brew.query.filter_by(name='hidden czech pilsener').first()
        user = BrewerProfile.get_by_email('hidden1@example.com')
        url = url_for('brew.labels', brew_id=brew.id)
        self.login(self.client, user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403
