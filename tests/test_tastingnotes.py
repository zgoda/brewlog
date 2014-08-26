from flask import url_for

from tests import BrewlogTestCase
from brewlog.models.brewing import Brew
from brewlog.models.tasting import TastingNote
from brewlog.models.users import BrewerProfile


class TastingNoteTestCase(BrewlogTestCase):

    def setUp(self):
        super(TastingNoteTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()
        self.hidden_brew_direct = Brew.query.filter_by(name='hidden czech pilsener').first()
        self.hidden_brew_indirect = Brew.query.filter_by(name='hidden amber ale').first()
        self.regular_user = BrewerProfile.get_by_email('user@example.com')

    def test_list_public_only(self):
        """
        Regular users can see only notes to public brews on the list
        """
        url = url_for('tastingnote-all')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertNotIn(self.hidden_brew_direct.absolute_url, rv.data)
            self.assertNotIn(self.hidden_brew_indirect.absolute_url, rv.data)

    def test_list_hidden_direct(self):
        url = url_for('tastingnote-all')
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_direct.brewery.brewer.email)
            rv = client.get(url)
            self.assertIn(self.hidden_brew_direct.absolute_url, rv.data)

    def test_list_hidden_indirect(self):
        url = url_for('tastingnote-all')
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_indirect.brewery.brewer.email)
            rv = client.get(url)
            self.assertIn(self.hidden_brew_indirect.absolute_url, rv.data)

    def test_create_anon(self):
        """
        Anonymous users can not add tasting notes
        """
        url = url_for('tastingnote-add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertEqual(rv.status_code, 302)

    def test_create_for_public_brew(self):
        """
        All logged in users can add tasting notes to public brews
        """
        url = url_for('tastingnote-add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.get(url)
            self.assertIn('<form', rv.data)
            data = {
                'text': 'Nice beer, cheers!'
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertIn(data['text'], rv.data)

    def test_create_for_hidden_brew_direct(self):
        """
        Users can not add tasting notes to hidden brews
        """
        url = url_for('tastingnote-add', brew_id=self.hidden_brew_direct.id)
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)
            data = {
                'text': 'Nice beer, cheers!'
            }
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_create_for_hidden_brew_indirect(self):
        """
        Users can not add tasting notes to brews of hidden brewery
        """
        url = url_for('tastingnote-add', brew_id=self.hidden_brew_indirect.id)
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)
            data = {
                'text': 'Nice beer, cheers!'
            }
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_delete_by_author(self):
        """
        Note author can delete it
        """
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-delete', note_id=note.id)
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertNotIn(note.text.encode('utf-8'), rv.data)

    def test_author_sees_delete_form(self):
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-delete', note_id=note.id)
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

    def test_delete_by_brew_owner(self):
        """
        Brew owner can delete tasting notes
        """
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-delete', note_id=note.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertNotIn(note.text.encode('utf-8'), rv.data)

    def test_delete_by_public(self):
        """
        Not involved in logged users can't delete notes
        """
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-delete', note_id=note.id)
        with self.app.test_client() as client:
            self.login(client, self.hidden_brew_indirect.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 403)


class TastingNoteAjaxTestCase(BrewlogTestCase):

    def setUp(self):
        super(TastingNoteAjaxTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()
        self.regular_user = BrewerProfile.get_by_email('user@example.com')
        self.url = url_for('tastingnote-loadtext')

    def test_load(self):
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        with self.app.test_client() as client:
            rv = client.get(self.url, query_string={'id': note.id})
            self.assertEqual(rv.status_code, 200)
            self.assertIn(note.text.encode('utf-8'), rv.data)

    def test_load_missing_id(self):
        with self.app.test_client() as client:
            rv = client.get(self.url)
            self.assertEqual(rv.status_code, 400)

    def test_load_nonexisting_note(self):
        with self.app.test_client() as client:
            rv = client.get(self.url, query_string={'id': 666})
            self.assertEqual(rv.status_code, 404)

    def test_anon_cant_edit_notes(self):
        """
        Anonymous user brew details view does not contain js to edit note texts
        """
        url = url_for('brew.details', brew_id=self.brew.id)
        edit_url = url_for('tastingnote-update')
        with self.app.test_client() as client:
            rv = client.get(url)
            self.assertNotIn(edit_url, rv.data)

    def test_update_note_by_public(self):
        """
        Anonymous users can not edit tasting note texts
        """
        note = TastingNote.create_for(self.brew, self.brew.brewery.brewer, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-update')
        data = {
            'id': note.id,
            'value': 'This brew is horrible!',
        }
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 403)

    def test_update_note_by_author(self):
        """
        Author can edit own notes
        """
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-update')
        data = {
            'id': note.id,
            'value': 'This brew is horrible!',
        }
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.post(url, data=data)
            note = TastingNote.query.get(note.id)
            self.assertEqual(rv.data, note.text_html)
            self.assertEqual(note.text, data['value'])

    def test_update_note_by_brew_owner(self):
        """
        Brew owner can edit notes to his brews regardless of note authorship
        """
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-update')
        data = {
            'id': note.id,
            'value': 'This brew is horrible!',
        }
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.post(url, data=data)
            note = TastingNote.query.get(note.id)
            self.assertEqual(rv.data, note.text_html)
            self.assertEqual(note.text, data['value'])

    def test_update_empty_text(self):
        note = TastingNote.create_for(self.brew, self.regular_user, 'Nice beer, cheers!', commit=True)
        url = url_for('tastingnote-update')
        data = {
            'id': note.id,
            'value': '',
        }
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.post(url, data=data)
            self.assertEqual(rv.data, note.text_html)

    def test_update_missing_id(self):
        url = url_for('tastingnote-update')
        data = {
            'value': 'This brew is horrible!',
        }
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 400)

    def test_update_nonexisting_note(self):
        url = url_for('tastingnote-update')
        data = {
            'id': 666,
            'value': 'This brew is horrible!',
        }
        with self.app.test_client() as client:
            self.login(client, self.regular_user.email)
            rv = client.post(url, data=data)
            self.assertEqual(rv.status_code, 404)
