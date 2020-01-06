import pytest
from flask import url_for

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestBreweryListView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.list_url = url_for('brewery.all')

    def brewery_url(self, brewery):
        return url_for('brewery.details', brewery_id=brewery.id)

    def delete_url(self, brewery):
        return url_for('brewery.delete', brewery_id=brewery.id)

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_nonowner(self, anonymous, user_factory, brewery_factory):
        public_user = user_factory(is_public=True)
        brewery_1 = brewery_factory(brewer=public_user)
        hidden_user = user_factory(is_public=False)
        brewery_2 = brewery_factory(brewer=hidden_user)
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(self.list_url)
        assert f'href="{self.brewery_url(brewery_1)}"' in rv.text
        assert f'href="{self.delete_url(brewery_1)}"' not in rv.text
        assert f'href="{self.brewery_url(brewery_2)}"' not in rv.text
        assert f'href="{self.delete_url(brewery_2)}"' not in rv.text
        add_url = url_for('brewery.add')
        assert bool(f'href="{add_url}"' in rv.text) is not anonymous

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_owner(self, public, user_factory, brewery_factory):
        actor = user_factory(is_public=public)
        brewery_1 = brewery_factory(brewer=actor)
        self.login(actor.email)
        hidden_user = user_factory(is_public=False)
        brewery_2 = brewery_factory(brewer=hidden_user)
        rv = self.client.get(self.list_url)
        assert f'href="{self.brewery_url(brewery_1)}"' in rv.text
        assert f'href="{self.delete_url(brewery_1)}"' in rv.text
        assert f'href="{self.brewery_url(brewery_2)}"' not in rv.text
        assert f'href="{self.delete_url(brewery_2)}"' not in rv.text


@pytest.mark.usefixtures('client_class')
class TestBreweryDetailsView(BrewlogTests):

    def url(self, brewery):
        return url_for('brewery.details', brewery_id=brewery.id)

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_get_nonowner_public(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert brewery.name in rv.text
        assert f'action="{url}"' not in rv.text

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_get_nonowner_hidden(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_get_owner(self, public, user_factory, brewery_factory):
        owner = user_factory(is_public=public)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        self.login(owner.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_post_nonowner_public(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        data = {'name': 'new name'}
        rv = self.client.post(url, data=data, follow_redirects=False)
        assert rv.status_code == 403

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_post_nonowner_hidden(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        data = {'name': 'new name'}
        rv = self.client.post(url, data=data, follow_redirects=False)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_post_owner(self, public, user_factory, brewery_factory):
        owner = user_factory(is_public=public)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        self.login(owner.email)
        url = self.url(brewery)
        name = 'new name'
        data = {'name': name}
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert f'<h3>{name}</h3>' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBreweryDeleteView(BrewlogTests):

    def url(self, brewery):
        return url_for('brewery.delete', brewery_id=brewery.id)

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_get_nonowner_public(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert rv.status_code == 403

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_get_nonowner_hidden(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_get_owner(self, public, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        self.login(owner.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert f'<h3>{brewery.name}</h3>' in rv.text
        assert f'action="{url}"' in rv.text

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_post_nonowner_public(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        data = {'delete_it': True}
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_post_nonowner_hidden(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        data = {'delete_it': True}
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_post_owner(self, public, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        self.login(owner.email)
        url = self.url(brewery)
        data = {'delete_it': True}
        rv = self.client.post(url, data=data)
        assert rv.status_code == 302
        assert url_for('profile.breweries', user_id=owner.id) in rv.headers['location']


@pytest.mark.usefixtures('client_class')
class TestBreweryCreateView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.url = url_for('brewery.add')

    def test_get_anon(self):
        rv = self.client.get(self.url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_get_authenticated(self, user_factory):
        actor = user_factory()
        self.login(actor.email)
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text

    def test_post_anon(self):
        data = {
            'name': 'brewery no 1'
        }
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_post_authenticated(self, user_factory):
        actor = user_factory()
        self.login(actor.email)
        name = 'brewery no 1'
        data = {'name': name}
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert f'<h3>{name}</h3>' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBreweryBrewsView(BrewlogTests):

    def url(self, brewery):
        return url_for('brewery.brews', brewery_id=brewery.id)

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_get_nonowner_public(
                self, anonymous, user_factory, brewery_factory, brew_factory
            ):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(name='brewery no 1', brewer=owner)
        public_brew = brew_factory(brewery=brewery, name='public brew', is_public=True)
        pb_url = url_for('brew.details', brew_id=public_brew.id)
        hidden_brew = brew_factory(brewery=brewery, name='hidden brew', is_public=False)
        hb_url = url_for('brew.details', brew_id=hidden_brew.id)
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(self.url(brewery))
        assert f'href="{pb_url}"' in rv.text
        assert f'href="{hb_url}"' not in rv.text

    @pytest.mark.parametrize('anonymous', [True, False], ids=['anon', 'actor'])
    def test_get_nonowner_hidden(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(name='brewery no 1', brewer=owner)
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        rv = self.client.get(self.url(brewery))
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_get_owner(self, public, user_factory, brewery_factory, brew_factory):
        owner = user_factory(is_public=public)
        brewery = brewery_factory(name='brewery no 1', brewer=owner)
        public_brew = brew_factory(brewery=brewery, name='public brew', is_public=True)
        pb_url = url_for('brew.details', brew_id=public_brew.id)
        hidden_brew = brew_factory(brewery=brewery, name='hidden brew', is_public=False)
        hb_url = url_for('brew.details', brew_id=hidden_brew.id)
        self.login(owner.email)
        rv = self.client.get(self.url(brewery))
        assert f'href="{pb_url}"' in rv.text
        assert f'href="{hb_url}"' in rv.text


@pytest.mark.usefixtures('client_class')
class TestJsonViews(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.endpoint = 'brewery.search'
        self.public_user = user_factory(is_public=True)
        self.public_brewery = brewery_factory(
            brewer=self.public_user, name='public brewery'
        )
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(
            brewer=self.hidden_user, name='hidden brewery'
        )

    def test_prefetch_anon(self):
        rv = self.client.get(url_for(self.endpoint))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == self.public_brewery.name

    def test_prefetch_authenticated(self):
        self.login(self.hidden_user.email)
        rv = self.client.get(url_for(self.endpoint))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == self.hidden_brewery.name

    def test_search_anon(self):
        rv = self.client.get(url_for(self.endpoint, q=self.public_brewery.name))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == self.public_brewery.name
        rv = self.client.get(url_for(self.endpoint, q=self.hidden_brewery.name))
        data = rv.get_json()
        assert len(data) == 0

    def test_search_authenticated(self, brewery_factory):
        self.login(self.hidden_user.email)
        rv = self.client.get(url_for(self.endpoint, q=self.hidden_brewery.name))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == self.hidden_brewery.name
        rv = self.client.get(url_for(self.endpoint, q=self.public_brewery.name))
        data = rv.get_json()
        assert len(data) == 0
