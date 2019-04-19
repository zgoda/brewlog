# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

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
    def test_nonowner_public(self, anonymous, user_factory, brewery_factory):
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
    def test_nonowner_hidden(self, anonymous, user_factory, brewery_factory):
        owner = user_factory(is_public=False)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        if not anonymous:
            actor = user_factory()
            self.login(actor.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public', [True, False], ids=['public', 'hidden'])
    def test_owner(self, public, user_factory, brewery_factory):
        owner = user_factory(is_public=public)
        brewery = brewery_factory(brewer=owner, name='brewery no 1')
        self.login(owner.email)
        url = self.url(brewery)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text
