import pytest
from flask import url_for

from brewlog.models import Brew, Brewery
from brewlog.utils.brewing import apparent_attenuation, real_attenuation

from . import BrewlogTests


class BrewTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, brewery_factory, user_factory):
        self.list_url = url_for('brew.all')
        self.create_url = url_for('brew.add')
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(
            brewer=self.public_user, name='public brewery no 1'
        )
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(
            brewer=self.hidden_user, name='hidden brewery no 2'
        )


@pytest.mark.usefixtures('client_class')
class TestBrewList(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

    def test_anon_user_view_list(self):
        """Anonymous user sees only public brews of public users. No brew
        action buttons are displayed.

        """

        rv = self.client.get(self.list_url)
        page = rv.data.decode('utf-8')
        assert self.public_brewery_public_brew.name in page
        assert self.public_brewery_hidden_brew.name not in page
        assert self.hidden_brewery_public_brew.name not in page
        assert self.hidden_brewery_hidden_brew.name not in page
        assert url_for('brew.delete', brew_id=self.public_brewery_public_brew.id) not in page

    def test_loggedin_public_user_view_list(self):
        """Logged in public user sees all his brews and public brews of public
        users. Brew action buttons are displayed only for his own brews.

        """

        self.login(self.public_user.email)
        rv = self.client.get(self.list_url)
        page = rv.data.decode('utf-8')
        assert self.public_brewery_public_brew.name in page
        assert self.public_brewery_hidden_brew.name in page
        assert self.hidden_brewery_public_brew.name not in page
        assert self.hidden_brewery_hidden_brew.name not in page
        assert url_for('brew.delete', brew_id=self.public_brewery_public_brew.id) in page
        assert url_for('brew.delete', brew_id=self.hidden_brewery_public_brew.id) not in page

    def test_loggedin_hidden_user_view_list(self):
        """Logged in hidden user sees all his brews and public brews of public
        users. Brew action buttons are displayed only for his own brews.

        """

        self.login(self.hidden_user.email)
        rv = self.client.get(self.list_url)
        page = rv.data.decode('utf-8')
        assert self.public_brewery_public_brew.name in page
        assert self.public_brewery_hidden_brew.name not in page
        assert self.hidden_brewery_public_brew.name in page
        assert self.hidden_brewery_hidden_brew.name in page
        assert url_for('brew.delete', brew_id=self.public_brewery_public_brew.id) not in page
        assert url_for('brew.delete', brew_id=self.hidden_brewery_public_brew.id) in page


@pytest.mark.usefixtures('client_class')
class TestBrewDetailsAnonUser(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

    def test_anon_user_public_brewery_public_brew_details(self):
        """Anonymous user sees read-only version of public brew details page.

        """

        brew_url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        action_text = 'action="{}"'.format(brew_url)
        rv = self.client.get(brew_url)
        assert action_text not in rv.data.decode('utf-8')

    def test_anon_user_public_brewery_hidden_brew_details(self):
        """Anonymous user gets 404 when trying to access public brewery hidden
        brew details page.

        """

        brew_url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        rv = self.client.get(brew_url)
        assert rv.status_code == 404

    def test_anon_user_hidden_brewery_public_brew_details(self):
        """Anonymous user gets 404 when trying to access hidden brewery public
        brew details page.

        """

        brew_url = url_for('brew.details', brew_id=self.hidden_brewery_public_brew.id)
        rv = self.client.get(brew_url)
        assert rv.status_code == 404

    def test_anon_user_hidden_brewery_hidden_brew_details(self):
        """Anonymous user gets 404 when trying to access hidden brewery hidden
        brew details page.

        """

        brew_url = url_for('brew.details', brew_id=self.hidden_brewery_hidden_brew.id)
        rv = self.client.get(brew_url)
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestBrewDetailsLoggedInUser(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

    def test_owner_public_brewery_public_brew_details(self):
        """Owner sees full version of own public brew details page.

        """

        self.login(self.public_user.email)
        brew_url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        action_text = 'action="{}"'.format(brew_url)
        rv = self.client.get(brew_url)
        assert action_text in rv.data.decode('utf-8')

    def test_owner_public_brewery_hidden_brew_details(self):
        """Owner sees full version of own hidden brew details page.

        """

        self.login(self.public_user.email)
        brew_url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        action_text = 'action="{}"'.format(brew_url)
        rv = self.client.get(brew_url)
        assert action_text in rv.data.decode('utf-8')

    def test_owner_hidden_brewery_public_brew_details(self):
        """Owner sees full version of own hidden brew details page.

        """

        self.login(self.hidden_user.email)
        brew_url = url_for('brew.details', brew_id=self.hidden_brewery_public_brew.id)
        action_text = 'action="{}"'.format(brew_url)
        rv = self.client.get(brew_url)
        assert action_text in rv.data.decode('utf-8')

    def test_owner_hidden_brewery_hidden_brew_details(self):
        """Owner sees full version of own hidden brew details page.

        """

        self.login(self.hidden_user.email)
        brew_url = url_for('brew.details', brew_id=self.hidden_brewery_hidden_brew.id)
        action_text = 'action="{}"'.format(brew_url)
        rv = self.client.get(brew_url)
        assert action_text in rv.data.decode('utf-8')

    def test_non_owner_hidden_brewery_public_brew_details(self):
        """Logged in user gets 404 when trying to access hidden brewery public
        brew details page.

        """

        self.login(self.public_user.email)
        brew_url = url_for('brew.details', brew_id=self.hidden_brewery_public_brew.id)
        rv = self.client.get(brew_url)
        assert rv.status_code == 404

    def test_non_owner_hidden_brewery_hidden_brew_details(self):
        """Logged in user gets 404 when trying to access hidden brewery hidden
        brew details page.

        """

        self.login(self.public_user.email)
        brew_url = url_for('brew.details', brew_id=self.hidden_brewery_hidden_brew.id)
        rv = self.client.get(brew_url)
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestBrewOperations(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )

    def test_anon_create_page(self):
        """Anonymous users can not access brew create page.

        """

        rv = self.client.get(self.create_url)
        assert rv.status_code == 302

    def test_add_form_visible_for_registered(self):
        """Registered users can access brew form.

        """

        self.login(self.public_user.email)
        rv = self.client.get(self.create_url)
        assert rv.status_code == 200
        assert 'action="%s"' % self.create_url in rv.data.decode('utf-8')

    def test_add_by_registered(self):
        """Registered users can add brews.

        """

        self.login(self.public_user.email)
        data = {
            'name': 'new brew',
            'brewery': self.public_brewery.id,
            'carbonation_type': 'bottles with priming',
            'carbonation_level': 'normal',
            'notes': 'new brew',
        }
        rv = self.client.post(self.create_url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        content = rv.data.decode('utf-8')
        assert '<h3>%s</h3>' % data['name'] in content
        assert self.public_brewery.name in content
        brew = Brew.query.filter_by(name=data['name']).first()
        assert brew.fermentation_steps.count() == 0

    def test_add_by_anon(self):
        """Anonymous users can not add brews.

        """

        data = {
            'name': 'new brew',
            'brewery': self.public_brewery.id,
            'carbonation_type': 'bottles with priming',
            'carbonation_level': 'normal',
            'notes': 'new brew',
        }
        rv = self.client.post(self.create_url, data=data, follow_redirects=False)
        assert rv.status_code == 302

    def test_add_by_non_owner(self):
        """Anonymous users can not add brews.

        """

        data = {
            'name': 'new brew extraorinaire no 1',
            'brewery': self.public_brewery.id,
            'carbonation_type': 'bottles with priming',
            'carbonation_level': 'normal',
            'notes': 'new brew',
        }
        self.login(self.hidden_user.email)
        rv = self.client.post(self.create_url, data=data, follow_redirects=False)
        assert rv.status_code == 200
        assert b'This field is required.' in rv.data
        assert Brew.query.filter_by(name=data['name']).first() is None

    def test_update_by_owner(self):
        """ Only brewery owner can update brew data.

        """

        url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        self.login(self.public_user.email)
        data = {
            'name': 'new name (still hidden)',
            'brewery': self.public_brewery.id,
            'carbonation_type': 'bottles with priming',
            'carbonation_level': 'normal',
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert '<h3>%s</h3>' % data['name'] in rv.data.decode('utf-8')

    def test_update_by_public(self):
        """ Non-owner can not update brew data

        """

        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        self.login(self.hidden_user.email)
        data = {
            'name': 'new name (still hidden)',
        }
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    def test_owner_access_delete_form(self):
        """Brew owner can access brew delete form.

        """

        url = url_for('brew.delete', brew_id=self.public_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert 'action="%s"' % url in rv.data.decode('utf-8')

    def test_delete_by_owner(self):
        """Owner can delete brew.

        """

        brew_id = self.public_brewery_hidden_brew.id
        url = url_for('brew.delete', brew_id=brew_id)
        self.login(self.public_user.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 200
        assert Brew.query.get(brew_id) is None

    def test_delete_by_non_owner(self):
        """Non-owner can not delete brew.

        """

        brew_id = self.public_brewery_hidden_brew.id
        url = url_for('brew.delete', brew_id=brew_id)
        self.login(self.hidden_user.email)
        rv = self.client.post(url, data={'delete_it': True})
        assert rv.status_code == 403
        assert Brew.query.get(brew_id) is not None

    def test_delete_by_anon(self):
        """Anonymous user can not delete brew.

        """

        brew_id = self.public_brewery_hidden_brew.id
        url = url_for('brew.delete', brew_id=brew_id)
        rv = self.client.post(url, data={'delete_it': True})
        assert rv.status_code == 302
        assert Brew.query.get(brew_id) is not None


@pytest.mark.usefixtures('client_class')
class TestBrewNavigation(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )

    def test_next_own_brews(self):
        brew_id = self.public_brewery_public_brew.id
        url = url_for('brew.details', brew_id=brew_id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        next_url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        assert '<a href="%s">next</a>' % next_url in content
        assert '>previous</a>' not in content

    def test_previous_own_brews(self):
        url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        prev_url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        assert '<a href="%s">previous</a>' % prev_url in rv.data.decode('utf-8')

    def test_anon_navigation(self):
        """Non-public brews are not accessible in prev/next navigation for
        anonymous user.

        """

        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id) not in content

    def test_non_owner_navigation(self):
        """Non-public brews are not accessible in prev/next navigation for
        non-owners.

        """

        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        content = rv.data.decode('utf-8')
        assert url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id) not in content


@pytest.mark.usefixtures('client_class')
class TestBrewObjectLists(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

    def test_list_public_only_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=True)]
        hidden_brews = [x.id for x in Brew.query.join(Brewery).filter(
            Brewery.brewer == self.public_user, Brew.is_public.is_(False)
        ).all()]
        for x in hidden_brews:
            assert x not in brew_ids

    def test_list_all_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=False)]
        assert len(brew_ids) == 2

    def test_list_public_in_hidden_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.hidden_user, public_only=True)]
        assert len(brew_ids) == 0

    def test_limit_public_only_in_public_brewery(self):
        limit = 0
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=True, limit=limit)]
        assert len(brew_ids) == limit

    def test_limit_all_in_public_brewery(self):
        limit = 1
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=False, limit=limit)]
        assert len(brew_ids) == limit


@pytest.mark.usefixtures('client_class')
class TestBrewAttenuation(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )

    def test_attenuation_none_display(self):
        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert b'apparent' not in rv.data

    def test_og_fg_set(self, fermentation_step_factory):
        fermentation_step_factory(brew=self.public_brewery_public_brew, og=10.5, fg=2.5, name='primary')
        brew = self.public_brewery_public_brew
        attenuation = brew.attenuation
        assert attenuation['apparent'] == apparent_attenuation(brew.og, brew.fg)
        assert attenuation['real'] == real_attenuation(brew.og, brew.fg)

    def test_no_og_no_fg(self, fermentation_step_factory):
        fermentation_step_factory(brew=self.public_brewery_public_brew, name='primary')
        assert self.public_brewery_public_brew.attenuation['apparent'] == 0
        assert self.public_brewery_public_brew.attenuation['real'] == 0

    def test_og_no_fg(self, fermentation_step_factory):
        fermentation_step_factory(brew=self.public_brewery_public_brew, name='primary', og=10)
        assert self.public_brewery_public_brew.attenuation['apparent'] == 0
        assert self.public_brewery_public_brew.attenuation['real'] == 0


@pytest.mark.usefixtures('client_class')
class TestBrewExport(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )

    def test_print_public(self):
        url = url_for('brew.print', brew_id=self.public_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200

    def test_print_hidden(self):
        url = url_for('brew.print', brew_id=self.hidden_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    def test_print_labels_public(self):
        url = url_for('brew.labels', brew_id=self.public_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert '%s</h3>' % self.public_brewery_public_brew.name in rv.data.decode('utf-8')

    def test_print_labels_custom_template(self, label_template_factory):
        template = label_template_factory(
            user=self.public_user, name='custom 1', text='#### {{ brew.name }}'
        )
        url = url_for('brew.labels', brew_id=self.public_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url, query_string={'template': template.id})
        assert rv.status_code == 200
        assert '<h4>%s</h4>' % self.public_brewery_public_brew.name in rv.data.decode('utf-8')

    def test_print_labels_hidden(self):
        url = url_for('brew.labels', brew_id=self.hidden_brewery_public_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403
