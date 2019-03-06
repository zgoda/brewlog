import datetime

import pytest
from flask import url_for

from brewlog.ext import db
from brewlog.models import Brew

from . import BrewlogTests


class BrewViewTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory(first_name='A', last_name='A')
        self.public_brewery = brewery_factory(name='public brewery no. 1', brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False, first_name='B', last_name='B')
        self.hidden_brewery = brewery_factory(name='hidden brewery no. 1', brewer=self.hidden_user)


@pytest.mark.usefixtures('client_class')
class TestBrewDetailsView(BrewViewTests):

    def url(self, brew):
        return url_for('brew.details', brew_id=brew.id)

    def test_get_404(self):
        rv = self.client.get(url_for('brew.details', brew_id=666))
        assert rv.status_code == 404

    def test_get_no_access_hidden_brewery(self, brew_factory):
        brew = brew_factory(brewery=self.hidden_brewery, name='hb1')
        self.login(self.public_user.email)
        rv = self.client.get(self.url(brew))
        assert rv.status_code == 404

    def test_get_no_access_hidden_brew(self, brew_factory):
        brew = brew_factory(brewery=self.public_brewery, is_public=False, name='hb1')
        self.login(self.hidden_user.email)
        rv = self.client.get(self.url(brew))
        assert rv.status_code == 404

    def test_post_data_ok(self, brew_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1', code='xxx')
        self.login(self.public_user.email)
        data = {
            'name': brew.name,
            'brewery': brew.brewery.id,
            'code': '001',
            'carbonation_level': 'low',
            'carbonation_type': 'bottles with priming',
        }
        rv = self.client.post(self.url(brew), data=data, follow_redirects=True)
        assert rv.status_code == 200
        assert 'data updated' in rv.data.decode('utf-8')
        assert Brew.query.get(brew.id).code == data['code']

    def test_post_data_missing(self, brew_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1', code='xxx')
        self.login(self.public_user.email)
        data = {
            'name': None,
            'brewery': brew.brewery.id,
            'code': '001',
            'carbonation_level': 'low',
            'carbonation_type': 'bottles with priming',
        }
        rv = self.client.post(self.url(brew), data=data, follow_redirects=True)
        assert rv.status_code == 200
        page = rv.data.decode('utf-8')
        assert 'field is required' in page
        assert 'data updated' not in page

    def test_state_form_present(self, brew_factory):
        brewed = datetime.date(1992, 12, 4)
        bottled = datetime.date(1993, 1, 12)
        taped = datetime.date(1993, 3, 8)
        brew = brew_factory(
            brewery=self.public_brewery, name='pb1', date_brewed=brewed,
            bottling_date=bottled, tapped=taped
        )
        self.login(self.public_user.email)
        rv = self.client.get(self.url(brew))
        page = rv.data.decode('utf-8')
        assert url_for('brew.chgstate', brew_id=brew.id) in page


@pytest.mark.usefixtures('client_class')
class TestJsonViews(BrewViewTests):

    def test_prefetch_anon(self, brew_factory):
        brew1 = brew_factory(brewery=self.public_brewery, name='pb1')
        brew_factory(brewery=self.hidden_brewery, name='hb2')
        rv = self.client.get(url_for('brew.search'))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == brew1.name

    def test_prefetch_auth(self, brew_factory):
        brew_factory(brewery=self.public_brewery, name='pb1')
        brew_h = brew_factory(brewery=self.public_brewery, name='hb2', is_public=False)
        self.login(self.public_user.email)
        rv = self.client.get(url_for('brew.search'))
        data = rv.get_json()
        assert len(data) == 2
        names = [x['name'] for x in data]
        assert brew_h.name in names

    def test_search_anon(self, brew_factory):
        brew_p = brew_factory(brewery=self.public_brewery, name='pb1')
        brew_h = brew_factory(brewery=self.public_brewery, name='hb2', is_public=False)
        rv = self.client.get(url_for('brew.search', q=brew_p.name))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == brew_p.name
        rv = self.client.get(url_for('brew.search', q=brew_h.name))
        data = rv.get_json()
        assert len(data) == 0

    def test_search_auth(self, brew_factory):
        brew_p = brew_factory(brewery=self.public_brewery, name='pb1')
        brew_h = brew_factory(brewery=self.public_brewery, name='hb2', is_public=False)
        self.login(self.public_user.email)
        rv = self.client.get(url_for('brew.search', q=brew_p.name))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == brew_p.name
        rv = self.client.get(url_for('brew.search', q=brew_h.name))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == brew_h.name


@pytest.mark.usefixtures('client_class')
class TestStateChangeView(BrewViewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.brew = brew_factory(
            brewery=self.public_brewery,
            name='pale ale',
            date_brewed=datetime.date.today() - datetime.timedelta(days=30),
            bottling_date=datetime.date.today() - datetime.timedelta(days=10),
        )
        self.url = url_for('brew.chgstate', brew_id=self.brew.id)

    def test_brew_tap_anon(self):
        rv = self.client.post(self.url, data=dict(action='tap'), follow_redirects=True)
        page = rv.data.decode('utf-8')
        assert 'Sign in with' in page

    def test_brew_tap_nonbrewer(self):
        self.login(self.hidden_user.email)
        rv = self.client.post(self.url, data=dict(action='tap'), follow_redirects=True)
        assert rv.status_code == 403
        page = rv.data.decode('utf-8')
        assert 'You don\'t have permission to access this page' in page

    def test_brew_tap_brewer(self):
        self.login(self.public_user.email)
        rv = self.client.post(self.url, data=dict(action='tap'), follow_redirects=True)
        page = rv.data.decode('utf-8')
        assert '</strong>: {}'.format(Brew.STATE_TAPPED) in page

    def test_brew_untap_brewer(self):
        self.brew.tapped = datetime.datetime.today() - datetime.timedelta(days=2)
        db.session.add(self.brew)
        db.session.commit()
        self.login(self.public_user.email)
        rv = self.client.post(self.url, data=dict(action='untap'), follow_redirects=True)
        page = rv.data.decode('utf-8')
        assert '</strong>: {}'.format(Brew.STATE_MATURING) in page

    def test_brew_finish_brewer(self):
        self.login(self.public_user.email)
        rv = self.client.post(self.url, data=dict(action='finish'), follow_redirects=True)
        page = rv.data.decode('utf-8')
        assert '</strong>: {}'.format(Brew.STATE_FINISHED) in page
