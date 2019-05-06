# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import datetime

import pytest
from flask import url_for

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestTastingNoteListView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)
        self.url = url_for('tastingnote.all')

    def test_get_anon(self, brew_factory, tasting_note_factory):
        public_brew = brew_factory(brewery=self.public_brewery, name='public_1')
        tasting_note_factory(brew=public_brew, author=self.public_user)
        tasting_note_factory(brew=public_brew, author=self.hidden_user)
        hidden_brew_1 = brew_factory(brewery=self.hidden_brewery, name='hidden_1')
        tasting_note_factory(brew=hidden_brew_1, author=self.hidden_user)
        hidden_brew_2 = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden_2'
        )
        tasting_note_factory(brew=hidden_brew_2, author=self.public_user)
        rv = self.client.get(self.url)
        assert f'{public_brew.name}</a>' in rv.text
        assert f'{hidden_brew_1.name}</a>' not in rv.text
        assert f'{hidden_brew_2.name}</a>' not in rv.text

    def test_get_authenticated(self, brew_factory, tasting_note_factory):
        public_brew = brew_factory(brewery=self.public_brewery, name='public_1')
        tasting_note_factory(brew=public_brew, author=self.public_user)
        tasting_note_factory(brew=public_brew, author=self.hidden_user)
        hidden_brew_1 = brew_factory(brewery=self.hidden_brewery, name='hidden_1')
        tasting_note_factory(brew=hidden_brew_1, author=self.hidden_user)
        hidden_brew_2 = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden_2'
        )
        tasting_note_factory(brew=hidden_brew_2, author=self.public_user)
        self.login(self.public_user.email)
        rv = self.client.get(self.url)
        assert f'{public_brew.name}</a>' in rv.text
        assert f'{hidden_brew_1.name}</a>' not in rv.text
        assert f'{hidden_brew_2.name}</a>' in rv.text


@pytest.mark.usefixtures('client_class')
class TestTastingNoteCreateView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory(is_public=True)
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_anon(self, public, brew_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=public)
        url = url_for('tastingnote.add', brew_id=brew.id)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_get_anon_hidden_indirect(self, brew_factory):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=True)
        url = url_for('tastingnote.add', brew_id=brew.id)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_anon(self, public, brew_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=public)
        data = {
            'text': 'Nice beer, cheers!',
            'date': datetime.date.today().isoformat(),
        }
        url = url_for('tastingnote.add', brew_id=brew.id)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_post_anon_hidden_indirect(self, brew_factory):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=True)
        data = {
            'text': 'Nice beer, cheers!',
            'date': datetime.date.today().isoformat(),
        }
        url = url_for('tastingnote.add', brew_id=brew.id)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_get_authenticated_to_public(self, brew_factory):
        brew = brew_factory(brewery=self.public_brewery)
        url = url_for('tastingnote.add', brew_id=brew.id)
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    @pytest.mark.parametrize('brewer,brew', [
        (True, True),
        (True, False),
        (False, True)
    ], ids=[])
    def test_get_authenticated_to_hidden(
                self, brewer, brew, brew_factory, user_factory
            ):
        if brewer is True:
            brewery = self.hidden_brewery
        else:
            brewery = self.public_brewery
        hidden_brew = not brew
        brew = brew_factory(brewery=brewery, is_public=hidden_brew)
        url = url_for('tastingnote.add', brew_id=brew.id)
        actor = user_factory()
        self.login(actor.email)
        rv = self.client.get(url)
        assert rv.status_code == 404
