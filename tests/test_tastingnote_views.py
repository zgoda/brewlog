import datetime

import pytest
from flask import url_for

from brewlog.models import TastingNote

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

    def test_post_authenticated_to_public(self, brew_factory, user_factory):
        brew = brew_factory(brewery=self.public_brewery)
        text = 'Nice beer, cheers!'
        data = {
            'text': text,
            'date': datetime.date.today().isoformat(),
        }
        url = url_for('tastingnote.add', brew_id=brew.id)
        actor = user_factory()
        self.login(actor.email)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert f'<p>{text}</p>' in rv.text

    @pytest.mark.parametrize('brewer,brew', [
        (True, True),
        (True, False),
        (False, True)
    ], ids=['hidden-hidden', 'hidden-public', 'public-hidden'])
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

    @pytest.mark.parametrize('brewer,brew', [
        (True, True),
        (True, False),
        (False, True)
    ], ids=['hidden-hidden', 'hidden-public', 'public-hidden'])
    def test_post_authenticated_to_hidden(
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
        text = 'Nice beer, cheers!'
        data = {
            'text': text,
            'date': datetime.date.today().isoformat(),
        }
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404


@pytest.mark.usefixtures('client_class')
class TestTastingNoteDeleteView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory(is_public=True)
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)
        self.author = user_factory()

    def url(self, note):
        return url_for('tastingnote.delete', note_id=note.id)

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_anon(self, public, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=public)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    @pytest.mark.parametrize('public_brew', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_anon_hidden_indirect(
                self, public_brew, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    @pytest.mark.parametrize('public', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_anon(self, public, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=public)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        data = {'delete_it': True}
        rv = self.client.post(url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    @pytest.mark.parametrize('public_brew', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_anon_hidden_indirect(
                self, public_brew, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        data = {'delete_it': True}
        rv = self.client.post(url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_get_authenticated_to_public(
                self, user_factory, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        actor = user_factory()
        url = self.url(note)
        self.login(actor.email)
        rv = self.client.get(url)
        assert rv.status_code == 403

    def test_post_authenticated_to_public(
                self, user_factory, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        actor = user_factory()
        url = self.url(note)
        data = {'delete_it': True}
        self.login(actor.email)
        rv = self.client.get(url, data=data)
        assert rv.status_code == 403

    def test_get_authenticated_to_hidden(
                self, user_factory, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, is_public=False)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        actor = user_factory()
        url = self.url(note)
        self.login(actor.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    def test_post_authenticated_to_hidden(
                self, user_factory, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, is_public=False)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        actor = user_factory()
        url = self.url(note)
        data = {'delete_it': True}
        self.login(actor.email)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_brew', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_authenticated_to_hidden_indirect(
                self, public_brew, user_factory, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        actor = user_factory()
        url = self.url(note)
        data = {'delete_it': True}
        self.login(actor.email)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404

    def test_get_author_to_public(self, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        self.login(self.author.email)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    def test_post_author_to_public(self, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        data = {'delete_it': True}
        self.login(self.author.email)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'has been deleted' in rv.text

    def test_get_author_to_hidden(self, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=False)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        self.login(self.author.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    def test_post_author_to_hidden(self, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=False)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        data = {'delete_it': True}
        self.login(self.author.email)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_brew', [
        True, False
    ], ids=['public', 'hidden'])
    def test_get_author_to_hidden_indirect(
                self, public_brew, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        self.login(self.author.email)
        rv = self.client.get(url)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_brew', [
        True, False
    ], ids=['public', 'hidden'])
    def test_post_author_to_hidden_indirect(
                self, public_brew, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.hidden_brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        data = {'delete_it': True}
        self.login(self.author.email)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ], ids=['public-public', 'public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_get_owner(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        self.login(brewery.brewer.email)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ], ids=['public-public', 'public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_post_owner(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        url = self.url(note)
        data = {'delete_it': True}
        self.login(brewery.brewer.email)
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert 'has been deleted' in rv.text


@pytest.mark.usefixtures('client_class')
class TestTastingNoteLoadView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)
        self.author = user_factory()
        self.url = url_for('tastingnote.loadtext')

    def test_missing_note_id(self):
        rv = self.client.get(self.url)
        assert rv.status_code == 400

    def test_nonexisting_note_id(self):
        rv = self.client.get(self.url, query_string={'id': 666})
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_anon(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        rv = self.client.get(self.url, query_string={'id': note.id})
        assert rv.status_code == 200
        assert note.text in rv.text

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_authenticated(
                self, public_brewery, public_brew,
                user_factory, brew_factory, tasting_note_factory,
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        actor = user_factory()
        self.login(actor.email)
        rv = self.client.get(self.url, query_string={'id': note.id})
        assert rv.status_code == 200
        assert note.text in rv.text

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_author(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        self.login(self.author.email)
        rv = self.client.get(self.url, query_string={'id': note.id})
        assert rv.status_code == 200
        assert note.text in rv.text

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ])
    def test_get_owner(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        self.login(brewery.brewer.email)
        rv = self.client.get(self.url, query_string={'id': note.id})
        assert rv.status_code == 200
        assert note.text in rv.text


@pytest.mark.usefixtures('client_class')
class TestTastingNoteUpdateView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)
        self.author = user_factory()
        self.url = url_for('tastingnote.update')

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ], ids=['public-public', 'public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_anon(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_authenticated_public(
                self, user_factory, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        actor = user_factory()
        self.login(actor.email)
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 403

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, False),
        (False, True),
        (False, False)
    ], ids=['public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_authenticated_hidden(
                self, public_brewery, public_brew,
                user_factory, brew_factory, tasting_note_factory,
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        actor = user_factory()
        self.login(actor.email)
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 404

    def test_author_public(
                self, brew_factory, tasting_note_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        self.login(self.author.email)
        rv = self.client.post(self.url, data=data)
        note = TastingNote.query.get(note.id)
        assert rv.text == note.text_html
        assert note.text == data['value']

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, False),
        (False, True),
        (False, False)
    ], ids=['public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_author_hidden(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        self.login(self.author.email)
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 404

    @pytest.mark.parametrize('public_brewery,public_brew', [
        (True, True),
        (True, False),
        (False, True),
        (False, False)
    ], ids=['public-public', 'public-hidden', 'hidden-public', 'hidden-hidden'])
    def test_owner(
                self, public_brewery, public_brew, brew_factory, tasting_note_factory
            ):
        if public_brewery:
            brewery = self.public_brewery
        else:
            brewery = self.hidden_brewery
        brew = brew_factory(brewery=brewery, is_public=public_brew)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        self.login(brewery.brewer.email)
        rv = self.client.post(self.url, data=data)
        note = TastingNote.query.get(note.id)
        assert rv.text == note.text_html
        assert note.text == data['value']

    def test_empty_text(self, brew_factory, tasting_note_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=True)
        note = tasting_note_factory(brew=brew, author=self.author, text='Good stuff')
        data = {
            'pk': note.id,
            'value': '',
        }
        self.login(self.author.email)
        rv = self.client.post(self.url, data=data)
        assert rv.text == note.text_html

    def test_missing_pk(self):
        data = {
            'value': 'This brew is horrible!',
        }
        self.login(self.author.email)
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 400

    def test_nonexisting_pk(self):
        data = {
            'pk': 666,
            'value': 'This brew is horrible!',
        }
        self.login(self.author.email)
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 404
