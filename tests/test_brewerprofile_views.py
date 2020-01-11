import pytest
from flask import url_for

from brewlog.models import BrewerProfile

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestBrewerProfileListAllView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('profile.all')

    def test_anon(self, user_factory):
        pu = user_factory(is_public=True)
        pu_url = url_for('profile.details', user_id=pu.id)
        hu = user_factory(is_public=False)
        hu_url = url_for('profile.details', user_id=hu.id)
        rv = self.client.get(self.url)
        assert f'href="{pu_url}"' in rv.text
        assert f'href="{hu_url}"' not in rv.text

    def test_authenticated_public(self, user_factory):
        pu = user_factory(is_public=True)
        pu_url = url_for('profile.details', user_id=pu.id)
        hu = user_factory(is_public=False)
        hu_url = url_for('profile.details', user_id=hu.id)
        self.login(pu.email)
        rv = self.client.get(self.url)
        assert f'href="{pu_url}"' in rv.text
        assert f'href="{hu_url}"' not in rv.text

    def test_authenticated_hidden(self, user_factory):
        pu = user_factory(is_public=True)
        pu_url = url_for('profile.details', user_id=pu.id)
        hu = user_factory(is_public=False)
        hu_url = url_for('profile.details', user_id=hu.id)
        self.login(hu.email)
        rv = self.client.get(self.url)
        assert f'href="{pu_url}"' in rv.text
        assert f'href="{hu_url}"' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBrewerProfileDetailsView(BrewlogTests):

    def url(self, user):
        return url_for('profile.details', user_id=user.id)

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_public_nonowner(self, anon, user_factory):
        user = user_factory(is_public=True)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(user)
        rv = self.client.get(url)
        assert f'action="{url}"' not in rv.text

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_hidden_nonowner(self, anon, user_factory):
        user = user_factory(is_public=False)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(user)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_owner(self, public, user_factory):
        user = user_factory(is_public=public)
        self.login(user.email)
        url = self.url(user)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_post_public_nonowner(self, anon, user_factory):
        user = user_factory(is_public=True)
        data = {
            'nick': 'wholly new nick',
            'email': user.email,
        }
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(user)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_post_hidden_nonowner(self, anon, user_factory):
        user = user_factory(is_public=False)
        data = {
            'nick': 'wholly new nick',
            'email': user.email,
        }
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(user)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_success_nick(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'nick': 'wholly new nick',
            'email': user.email,
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'profile data has been updated' in rv.text

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_success_name(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'first_name': 'Special',
            'last_name': 'Case',
            'email': user.email,
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'profile data has been updated' in rv.text

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_fail_email_missing(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'nick': 'wholly new nick',
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'This field is required' in rv.text
        assert 'is-invalid' in rv.text

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_fail_name_and_nick(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'email': user.email,
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'please provide full name or nick'

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_fail_last_name(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'email': user.email,
            'first_name': 'Corner',
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'please provide full name or nick'

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_fail_first_name(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'email': user.email,
            'last_name': 'Case',
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'is-invalid' in rv.text
        assert 'please provide full name or nick'

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner_fail_email_invalid(self, public, user_factory):
        user = user_factory(is_public=public)
        data = {
            'nick': 'wholly new nick',
            'email': 'garbage',
        }
        self.login(user.email)
        url = self.url(user)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'is not valid email address' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBrewerProfileDeleteView(BrewlogTests):

    def url(self, user):
        return url_for('profile.delete', user_id=user.id)

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_owner(self, public, user_factory):
        user = user_factory(is_public=public)
        self.login(user.email)
        url = self.url(user)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_public_nonowner(self, anon, user_factory):
        user = user_factory(is_public=True)
        url = self.url(user)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(url)
        if anon:
            assert rv.status_code == 302
        else:
            assert rv.status_code == 403

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_hidden_nonowner(self, anon, user_factory):
        user = user_factory(is_public=False)
        url = self.url(user)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(url)
        if anon:
            assert rv.status_code == 302
        else:
            assert rv.status_code == 404

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_owner(self, public, user_factory):
        data = {
            'delete_it': True,
        }
        user = user_factory(is_public=public)
        user_id = user.id
        self.login(user.email)
        url = self.url(user)
        self.client.post(url, data=data)
        assert BrewerProfile.query.get(user_id) is None

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_post_public_nonowner(self, anon, user_factory):
        data = {
            'delete_it': True,
        }
        user = user_factory(is_public=True)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(user)
        rv = self.client.post(url, data=data)
        if anon:
            assert rv.status_code == 302
        else:
            assert rv.status_code == 403

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_post_hidden_nonowner(self, anon, user_factory):
        data = {
            'delete_it': True,
        }
        user = user_factory(is_public=False)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(user)
        rv = self.client.post(url, data=data)
        if anon:
            assert rv.status_code == 302
        else:
            assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestBrewerProfileBreweryListView(BrewlogTests):

    def url(self, user):
        return url_for('profile.breweries', user_id=user.id)

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_public_nonowner(self, anon, user_factory, brewery_factory):
        user = user_factory(is_public=True)
        brewery = brewery_factory(brewer=user)
        brewery_details_url = url_for('brewery.details', brewery_id=brewery.id)
        brewery_delete_url = url_for('brewery.delete', brewery_id=brewery.id)
        url = self.url(user)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(url)
        assert f'href="{brewery_details_url}"' in rv.text
        assert f'href="{brewery_delete_url}"' not in rv.text

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_hidden_nonowner(self, anon, user_factory, brewery_factory):
        user = user_factory(is_public=False)
        brewery_factory(brewer=user)
        url = self.url(user)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_owner(self, public, user_factory, brewery_factory):
        user = user_factory(is_public=public)
        brewery = brewery_factory(brewer=user)
        brewery_details_url = url_for('brewery.details', brewery_id=brewery.id)
        brewery_delete_url = url_for('brewery.delete', brewery_id=brewery.id)
        url = self.url(user)
        self.login(user.email)
        rv = self.client.get(url)
        assert f'href="{brewery_details_url}"' in rv.text
        assert f'href="{brewery_delete_url}"' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBrewerProfileBrewListView(BrewlogTests):

    def url(self, user):
        return url_for('profile.brews', user_id=user.id)

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_public_nonowner(
                self, anon, user_factory, brewery_factory, brew_factory
            ):
        user = user_factory(is_public=True)
        brewery = brewery_factory(brewer=user)
        brew = brew_factory(brewery=brewery, is_public=True)
        brew_details_url = url_for('brew.details', brew_id=brew.id)
        brew_delete_url = url_for('brew.delete', brew_id=brew.id)
        url = self.url(user)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(url)
        assert f'href="{brew_details_url}"' in rv.text
        assert f'href="{brew_delete_url}"' not in rv.text

    @pytest.mark.parametrize('anon', [
        True, False,
    ], ids=['anon', 'authenticated'])
    def test_get_hidden_nonowner(self, anon, user_factory):
        user = user_factory(is_public=False)
        url = self.url(user)
        if not anon:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_user,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ], ids=['public-public', 'public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_get_owner(
                self, public_user, public_brew,
                user_factory, brewery_factory, brew_factory
            ):
        user = user_factory(is_public=public_user)
        brewery = brewery_factory(brewer=user)
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        brew_details_url = url_for('brew.details', brew_id=brew.id)
        brew_delete_url = url_for('brew.delete', brew_id=brew.id)
        url = self.url(user)
        self.login(user.email)
        rv = self.client.get(url)
        assert f'href="{brew_details_url}"' in rv.text
        assert f'href="{brew_delete_url}"' in rv.text


@pytest.mark.usefixtures('client_class')
class TestSetPasswordView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('profile.setpassword')

    def test_anon_get(self):
        rv = self.client.get(self.url, follow_redirects=False)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['Location']

    def test_authenticated_get(self, user_factory):
        user = user_factory()
        self.login(user.email)
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text

    def test_post_ok(self, user_factory):
        old_password = 'pass1'
        new_password = 'pass2'
        user = user_factory(password=old_password)
        self.login(user.email)
        data = {
            'new_password': new_password,
            'new_password_r': new_password
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'your password has been changed' in rv.text
        assert BrewerProfile.query.get(user.id).check_password(new_password)

    @pytest.mark.parametrize('password', ['', 'garbage'], ids=['empty', 'garbage'])
    def test_post_fail(self, password, user_factory):
        old_password = 'pass1'
        new_password = 'pass2'
        user = user_factory(password=old_password)
        self.login(user.email)
        data = {
            'new_password': new_password,
            'new_password_r': password
        }
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert 'your password has been changed' not in rv.text
        assert BrewerProfile.query.get(user.id).check_password(old_password)
