import datetime

from flask import url_for
import pytest

from brewlog.models import TastingNote

from . import BrewlogTests


class TastingTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, tasting_note_factory, brew_factory, brewery_factory, user_factory):
        self.extra_user = user_factory()
        # public user data
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(
            brewer=self.public_user, name='public brewery no 1'
        )
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )

        # hidden user data
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(
            brewer=self.hidden_user, name='hidden brewery no 2'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

        self.list_url = url_for('tastingnote.all')

        self.pbpb_note_1 = tasting_note_factory(
            brew=self.public_brewery_public_brew,
            author=self.public_user,
        )
        self.pbpb_note_2 = tasting_note_factory(
            brew=self.public_brewery_public_brew,
            author=self.extra_user,
        )
        self.pbpb_note_3 = tasting_note_factory(
            brew=self.public_brewery_public_brew,
            author=self.hidden_user,
        )
        self.pbhb_note_1 = tasting_note_factory(
            brew=self.public_brewery_hidden_brew,
            author=self.public_user,
        )
        self.hbhb_note_1 = tasting_note_factory(
            brew=self.hidden_brewery_public_brew,
            author=self.hidden_user,
        )

        self.ajax_load_url = url_for('tastingnote.loadtext')


@pytest.mark.usefixtures('app')
class TestTastingNoteModel(TastingTests):

    def test_create_for_with_date(self, user_factory, mocker):
        date = datetime.date(year=1992, month=12, day=4)
        user = user_factory()
        text = 'note X'
        note = TastingNote.create_for(
            self.public_brewery_public_brew, author=user, text=text, date=date
        )
        assert note.date == date

    def test_create_for_no_date(self, user_factory, mocker):
        user = user_factory()
        date = datetime.date(year=1992, month=12, day=4)
        fake_datetime = mocker.MagicMock()
        fake_datetime.date.today.return_value = date
        mocker.patch(
            'brewlog.models.tasting.datetime',
            fake_datetime,
        )
        text = 'note X'
        note = TastingNote.create_for(
            self.public_brewery_public_brew, author=user, text=text
        )
        assert note.date == date


@pytest.mark.usefixtures('client_class')
class TestTastingNote(TastingTests):

    def test_list_anon(self):
        """Anonymous users can see only notes to public brews on the list.

        """

        rv = self.client.get(self.list_url)
        assert self.public_brewery_hidden_brew.name not in rv.text
        assert self.hidden_brewery_public_brew.name not in rv.text
        assert self.hidden_user.full_name in rv.text

    def test_list_logged_in(self):
        self.login(self.public_user.email)
        rv = self.client.get(self.list_url)
        assert self.public_brewery_public_brew.name in rv.text
        assert self.public_brewery_hidden_brew.name in rv.text
        assert self.hidden_user.full_name in rv.text
        assert self.hidden_brewery_public_brew.name not in rv.text
        assert self.hidden_brewery_hidden_brew.name not in rv.text

    def test_create_anon(self):
        """
        Anonymous users can not add tasting notes
        """
        url = url_for('tastingnote.add', brew_id=self.public_brewery_public_brew.id)
        rv = self.client.get(url)
        assert rv.status_code == 302

    def test_create_for_public_brew(self):
        """
        All logged in users can add tasting notes to public brews
        """
        url = url_for('tastingnote.add', brew_id=self.public_brewery_public_brew.id)
        self.login(self.extra_user.email)
        rv = self.client.get(url)
        assert f'action="{url}"' in rv.text
        data = {
            'text': 'Nice beer, cheers!',
            'date': datetime.date.today().isoformat(),
        }
        rv = self.client.post(url, data=data, follow_redirects=True)
        assert data['text'] in rv.text

    def test_create_for_hidden_brew_direct(self):
        """
        Users can not add tasting notes to hidden brews
        """
        url = url_for('tastingnote.add', brew_id=self.public_brewery_hidden_brew.id)
        self.login(self.extra_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403
        data = {
            'text': 'Nice beer, cheers!'
        }
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    def test_create_for_hidden_brew_indirect(self):
        """
        Users can not add tasting notes to brews of hidden brewery
        """
        url = url_for('tastingnote.add', brew_id=self.hidden_brewery_public_brew.id)
        self.login(self.extra_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 403
        data = {
            'text': 'Nice beer, cheers!'
        }
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    def test_delete_by_author(self):
        """
        Note author can delete it
        """
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.delete', note_id=note.id)
        self.login(self.public_user.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert note.text not in rv.text

    def test_author_sees_delete_form(self):
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.delete', note_id=note.id)
        self.login(self.extra_user.email)
        rv = self.client.get(url)
        assert rv.status_code == 200
        assert f'action="{url}"' in rv.text

    def test_delete_by_brew_owner(self):
        """
        Brew owner can delete tasting notes
        """
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.delete', note_id=note.id)
        self.login(self.public_user.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert note.text not in rv.text

    def test_delete_by_public(self):
        """
        Not involved in logged users can't delete notes
        """
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.delete', note_id=note.id)
        self.login(self.hidden_user.email)
        rv = self.client.post(url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 403


@pytest.mark.usefixtures('client_class')
class TestTastingNoteAjax(TastingTests):

    def test_load(self):
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        rv = self.client.get(self.ajax_load_url, query_string={'id': note.id})
        assert rv.status_code == 200
        assert note.text in rv.text

    def test_load_missing_id(self):
        rv = self.client.get(self.ajax_load_url)
        assert rv.status_code == 400

    def test_load_nonexisting_note(self):
        rv = self.client.get(self.ajax_load_url, query_string={'id': 666})
        assert rv.status_code == 404

    def test_anon_cant_edit_notes(self):
        """
        Anonymous user brew details view does not contain js to edit note texts
        """
        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        edit_url = url_for('tastingnote.update')
        rv = self.client.get(url)
        assert edit_url not in rv.text

    def test_update_note_by_public(self):
        """
        Anonymous users can not edit tasting note texts
        """
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.update')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        self.login(self.hidden_user.email)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 403

    def test_update_note_by_author(self):
        """
        Author can edit own notes
        """
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote.update')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        self.login(self.extra_user.email)
        rv = self.client.post(url, data=data)
        note = TastingNote.query.get(note.id)
        assert rv.text == note.text_html
        assert note.text == data['value']

    def test_update_note_by_brew_owner(self):
        """
        Brew owner can edit notes to his brews regardless of note authorship
        """
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.update')
        data = {
            'pk': note.id,
            'value': 'This brew is horrible!',
        }
        self.login(self.public_user.email)
        rv = self.client.post(url, data=data)
        note = TastingNote.query.get(note.id)
        assert rv.text == note.text_html
        assert note.text == data['value']

    def test_update_empty_text(self):
        note = TastingNote.create_for(
            self.public_brewery_public_brew, self.extra_user, 'Nice beer, cheers!', commit=True
        )
        url = url_for('tastingnote.update')
        data = {
            'pk': note.id,
            'value': '',
        }
        self.login(self.public_user.email)
        rv = self.client.post(url, data=data)
        assert rv.text == note.text_html

    def test_update_missing_id(self):
        url = url_for('tastingnote.update')
        data = {
            'value': 'This brew is horrible!',
        }
        self.login(self.extra_user.email)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 400

    def test_update_nonexisting_note(self):
        url = url_for('tastingnote.update')
        data = {
            'pk': 666,
            'value': 'This brew is horrible!',
        }
        self.login(self.extra_user.email)
        rv = self.client.post(url, data=data)
        assert rv.status_code == 404
