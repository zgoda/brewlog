import datetime

from flask import url_for

from brewlog.tests import BrewlogTestCase
from brewlog.models.brewing import Brew
from brewlog.models.calendar import Event
from brewlog.models.users import BrewerProfile


class CalendarTestCase(BrewlogTestCase):

    def setUp(self):
        super(CalendarTestCase, self).setUp()
        self.brew = Brew.query.filter_by(name='pale ale').first()
        self.other_brewer = BrewerProfile.get_by_email('hidden1@example.com')

    def test_add_by_owner(self):
        url = url_for('brew-brewevent_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            date = datetime.datetime.utcnow()
            data = {
                'title': 'gravity check',
                'description': '1.048 at 20*C',
                'date': date.strftime('%Y-%m-%d'),
                'event_type': 'gravity check',
                'is_public': True,
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(Event.query.filter_by(brew=self.brew).count(), 3)

    def test_others_cant_add(self):
        url = url_for('brew-brewevent_add', brew_id=self.brew.id)
        with self.app.test_client() as client:
            self.login(client, self.other_brewer.email)
            date = datetime.datetime.utcnow()
            data = {
                'title': 'gravity check',
                'description': '1.048 at 20*C',
                'date': date.strftime('%Y-%m-%d'),
                'event_type': 'gravity check',
                'is_public': True,
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

    def test_owner_sees_edit_form(self):
        event = Event.query.filter_by(brew=self.brew).first()
        url = url_for('brew-brew_event', event_id=event.id)
        with self.app.test_client() as client:
            self.login(client, event.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

    def test_others_cant_access_edit_form(self):
        event = Event.query.filter_by(brew=self.brew).first()
        url = url_for('brew-brew_event', event_id=event.id)
        with self.app.test_client() as client:
            self.login(client, self.other_brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_modify(self):
        event = Event.query.filter_by(brew=self.brew).first()
        url = url_for('brew-brew_event', event_id=event.id)
        with self.app.test_client() as client:
            self.login(client, event.brew.brewery.brewer.email)
            data = {
                'title': 'gravity check',
                'description': '1.048 at 20*C',
                'date': event.date.strftime('%Y-%m-%d'),
                'event_type': 'gravity check',
                'is_public': True,
            }
            rv = client.post(url, data=data, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(data['title'], rv.data)
            event = Event.query.get(event.id)
            self.assertEqual(event.title, data['title'])

    def test_owner_sees_delete_form(self):
        event = Event.query.filter_by(brew=self.brew).first()
        url = url_for('brew-brewevent_delete', event_id=event.id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 200)
            self.assertIn('action="%s"' % url, rv.data)

    def test_others_cant_access_delete_form(self):
        event = Event.query.filter_by(brew=self.brew).first()
        url = url_for('brew-brewevent_delete', event_id=event.id)
        with self.app.test_client() as client:
            self.login(client, self.other_brewer.email)
            rv = client.get(url)
            self.assertEqual(rv.status_code, 403)

    def test_delete(self):
        event = Event.query.filter_by(brew=self.brew).first()
        event_id = event.id
        url = url_for('brew-brewevent_delete', event_id=event_id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': True}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIsNone(Event.query.get(event_id))

    def test_delete_attempt_not_checked(self):
        event = Event.query.filter_by(brew=self.brew).first()
        event_id = event.id
        url = url_for('brew-brewevent_delete', event_id=event_id)
        with self.app.test_client() as client:
            self.login(client, self.brew.brewery.brewer.email)
            rv = client.post(url, data={'delete_it': 'false'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIsNotNone(Event.query.get(event_id))


class EventListsTestCase(BrewlogTestCase):

    def setUp(self):
        super(EventListsTestCase, self).setUp()
        self.user = BrewerProfile.get_by_email('user1@example.com')
        self.hidden = BrewerProfile.get_by_email('hidden0@example.com')

    def test_list_all_in_public_brewery(self):
        ids = [x.id for x in Event.get_latest_for(self.user, public_only=False)]
        self.assertEqual(len(ids), 2)

    def test_list_public_in_public_brewery(self):
        ids = [x.id for x in Event.get_latest_for(self.user, public_only=True)]
        self.assertEqual(len(ids), 1)

    def test_list_in_hidden_brewery(self):
        self.assertEqual(len(Event.get_latest_for(self.hidden, public_only=True)), 0)

    def test_limit(self):
        limit = 1
        self.assertEqual(len(Event.get_latest_for(self.user, public_only=False, limit=limit)), limit)
