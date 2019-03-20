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
        public_brew = brew_factory(brewery=self.public_brewery)
        tasting_note_factory(brew=public_brew, author=self.public_user)
        tasting_note_factory(brew=public_brew, author=self.hidden_user)
        hidden_brew_1 = brew_factory(brewery=self.hidden_brewery)
        tasting_note_factory(brew=hidden_brew_1, author=self.hidden_user)
        hidden_brew_2 = brew_factory(brewery=self.public_brewery, is_public=False)
        tasting_note_factory(brew=hidden_brew_2, author=self.public_user)
        rv = self.client.get(self.url)
        assert f'tasted {public_brew.name}' in rv.text
        assert f'tasted {hidden_brew_1.name}' not in rv.text
        assert f'tasted {hidden_brew_2.name}' not in rv.text

    def test_get_authenticated(self, brew_factory, tasting_note_factory):
        public_brew = brew_factory(brewery=self.public_brewery)
        tasting_note_factory(brew=public_brew, author=self.public_user)
        tasting_note_factory(brew=public_brew, author=self.hidden_user)
        hidden_brew_1 = brew_factory(brewery=self.hidden_brewery)
        tasting_note_factory(brew=hidden_brew_1, author=self.hidden_user)
        hidden_brew_2 = brew_factory(brewery=self.public_brewery, is_public=False)
        tasting_note_factory(brew=hidden_brew_2, author=self.public_user)
        self.login(self.public_user.email)
        rv = self.client.get(self.url)
        assert f'tasted {public_brew.name}' in rv.text
        assert f'tasted {hidden_brew_1.name}' not in rv.text
        assert f'tasted {hidden_brew_2.name}' in rv.text


@pytest.mark.usefixtures('client_class')
class TestTastingNoteCreateView(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)

    def test_get_create_anon_to_public(self, brew_factory):
        brew = brew_factory(brewery=self.public_brewery)
        url = url_for('tastingnote.add', brew_id=brew.id)
        rv = self.client.get(url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']
