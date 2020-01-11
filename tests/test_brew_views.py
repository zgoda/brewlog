import datetime

import pytest
from flask import url_for

from brewlog.ext import db
from brewlog.models import Brew

from . import BrewlogTests


class BrewViewTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory(
            first_name='John', last_name='Public'
        )
        self.public_brewery = brewery_factory(
            name='public brewery', brewer=self.public_user
        )
        self.hidden_user = user_factory(
            is_public=False, first_name='Rebecca', last_name='Hidden'
        )
        self.hidden_brewery = brewery_factory(
            name='hidden brewery', brewer=self.hidden_user
        )


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
        brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hb1'
        )
        self.login(self.hidden_user.email)
        rv = self.client.get(self.url(brew))
        assert rv.status_code == 404

    def test_post_anon(self, brew_factory):
        brew = brew_factory(
            brewery=self.public_brewery, name='pb1', code='xxx'
        )
        data = {
            'name': brew.name,
            'brewery': brew.brewery.id,
            'code': '001',
            'carbonation_level': 'low',
            'carbonation_type': 'bottles with priming',
        }
        rv = self.client.post(self.url(brew), data=data)
        assert rv.status_code == 403

    def test_post_non_brewer(self, brew_factory):
        brew = brew_factory(
            brewery=self.public_brewery, name='pb1', code='xxx'
        )
        self.login(self.hidden_user.email)
        data = {
            'name': brew.name,
            'brewery': brew.brewery.id,
            'code': '001',
            'carbonation_level': 'low',
            'carbonation_type': 'bottles with priming',
        }
        rv = self.client.post(self.url(brew), data=data, follow_redirects=True)
        assert rv.status_code == 403

    def test_post_data_ok(self, brew_factory):
        brew = brew_factory(
            brewery=self.public_brewery, name='pb1', code='xxx'
        )
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
        assert 'data updated' in rv.text
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
        assert 'field is required' in rv.text
        assert 'data updated' not in rv.text

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
        assert url_for('brew.chgstate', brew_id=brew.id) in rv.text

    def test_attenuation_display_none(self, brew_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
        self.login(self.public_user.email)
        rv = self.client.get(self.url(brew))
        assert 'apparent' not in rv.text


@pytest.mark.usefixtures('client_class')
class TestBrewDetailsNavigation(BrewViewTests):

    def url(self, brew):
        return url_for('brew.details', brew_id=brew.id)

    @pytest.mark.parametrize('anon', [
        False, True,
    ], ids=['authenticated', 'anonymous'])
    def test_brew_navigation_non_owner(self, anon, brew_factory):
        p2_brew = brew_factory(brewery=self.public_brewery)
        p1_brew = brew_factory(brewery=self.public_brewery, is_public=False)
        brew = brew_factory(brewery=self.public_brewery)
        n1_brew = brew_factory(brewery=self.public_brewery, is_public=False)
        n2_brew = brew_factory(brewery=self.public_brewery)
        if not anon:
            self.login(self.hidden_user.email)
        rv = self.client.get(self.url(brew))
        assert f'href="{self.url(p2_brew)}"' in rv.text
        assert f'href="{self.url(p1_brew)}"' not in rv.text
        assert f'href="{self.url(n1_brew)}"' not in rv.text
        assert f'href="{self.url(n2_brew)}"' in rv.text

    def test_brew_navigation_owner(self, brew_factory):
        p1_brew = brew_factory(brewery=self.public_brewery, is_public=False)
        brew = brew_factory(brewery=self.public_brewery)
        n1_brew = brew_factory(brewery=self.public_brewery, is_public=False)
        self.login(self.public_user.email)
        rv = self.client.get(self.url(brew))
        assert f'href="{self.url(p1_brew)}"' in rv.text
        assert f'href="{self.url(n1_brew)}"' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBrewListView(BrewViewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self):
        self.url = url_for('brew.all')

    def details_url(self, brew):
        return url_for('brew.details', brew_id=brew.id)

    def delete_url(self, brew):
        return url_for('brew.delete', brew_id=brew.id)

    def test_anon(self, brew_factory):
        hb_hb = brew_factory(brewery=self.hidden_brewery, is_public=False)
        pb_hb = brew_factory(brewery=self.hidden_brewery, is_public=True)
        pb_pb = brew_factory(brewery=self.public_brewery, is_public=True)
        hb_pb = brew_factory(brewery=self.public_brewery, is_public=False)
        rv = self.client.get(self.url)
        assert url_for('brew.details', brew_id=pb_pb.id) in rv.text
        assert url_for('brew.delete', brew_id=pb_pb.id) not in rv.text
        assert url_for('brew.details', brew_id=hb_hb.id) not in rv.text
        assert url_for('brew.details', brew_id=pb_hb.id) not in rv.text
        assert url_for('brew.details', brew_id=hb_pb.id) not in rv.text

    def test_authenticated(self, user_factory, brewery_factory, brew_factory):
        user2 = user_factory(first_name='Ivory', last_name='Tower')
        brewery2 = brewery_factory(brewer=user2, name='brewery2')
        pb1 = brew_factory(brewery=self.public_brewery)
        pb2 = brew_factory(brewery=brewery2)
        hb1 = brew_factory(name='hidden1', brewery=self.public_brewery, is_public=False)
        hb2 = brew_factory(name='hidden2', brewery=brewery2, is_public=False)
        hb3 = brew_factory(name='hidden3', brewery=self.hidden_brewery)
        hb4 = brew_factory(name='hidden4', brewery=self.hidden_brewery, is_public=False)
        self.login(email=self.public_user.email)
        rv = self.client.get(self.url)
        assert f'href="{self.details_url(pb1)}"' in rv.text
        assert f'href="{self.delete_url(pb1)}"' in rv.text
        assert f'href="{self.details_url(pb2)}"' in rv.text
        assert f'href="{self.delete_url(pb2)}"' not in rv.text
        assert f'href="{self.details_url(hb1)}"' in rv.text
        assert f'href="{self.details_url(hb2)}"' not in rv.text
        assert f'href="{self.details_url(hb3)}"' not in rv.text
        assert f'href="{self.details_url(hb4)}"' not in rv.text


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
        rv = self.client.post(self.url, data={'action': 'tap'})
        assert url_for('auth.select') in rv.headers['Location']

    def test_brew_tap_nonbrewer(self):
        self.login(self.hidden_user.email)
        rv = self.client.post(self.url, data={'action': 'tap'}, follow_redirects=True)
        assert rv.status_code == 403
        assert "You don't have permission to access this page" in rv.text

    def test_brew_tap_brewer(self):
        self.login(self.public_user.email)
        rv = self.client.post(self.url, data={'action': 'tap'}, follow_redirects=True)
        assert f'</strong>: {Brew.STATE_TAPPED}' in rv.text
        assert 'state changed' in rv.text

    def test_brew_untap_brewer(self):
        self.brew.tapped = datetime.datetime.today() - datetime.timedelta(days=2)
        db.session.add(self.brew)
        db.session.commit()
        self.login(self.public_user.email)
        rv = self.client.post(
            self.url, data={'action': 'untap'}, follow_redirects=True
        )
        assert f'</strong>: {Brew.STATE_MATURING}' in rv.text
        assert 'state changed' in rv.text

    def test_brew_finish_brewer(self):
        self.login(self.public_user.email)
        rv = self.client.post(
            self.url, data={'action': 'finish'}, follow_redirects=True
        )
        assert f'</strong>: {Brew.STATE_FINISHED}' in rv.text
        assert 'state changed' in rv.text
        assert self.brew.tapped is None

    def test_invalid_state(self):
        self.login(self.public_user.email)
        rv = self.client.post(
            self.url, data={'action': 'dummy'}, follow_redirects=True
        )
        assert 'invalid state' in rv.text


@pytest.mark.usefixtures('client_class')
class TestBrewAddView(BrewViewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self):
        self.url = url_for('brew.add')

    def test_get_anon(self):
        rv = self.client.get(self.url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_get_authenticated(self):
        self.login(email=self.public_user.email)
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text

    def test_post_anon(self):
        data = {
            'name': 'pale ale',
            'brewery': self.public_brewery.id,
            'carbonation_type': 'keg with priming',
            'carbonation_level': 'low',
        }
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['location']

    def test_post_authenticated_own_brewery(self):
        name = 'pale ale'
        data = {
            'name': name,
            'brewery': self.public_brewery.id,
            'carbonation_type': 'keg with priming',
            'carbonation_level': 'low',
        }
        self.login(email=self.public_user.email)
        rv = self.client.post(self.url, data=data, follow_redirects=True)
        assert f'{name} created' in rv.text

    def test_post_authenticated_other_brewery(self):
        data = {
            'name': 'pale ale',
            'brewery': self.public_brewery.id,
            'carbonation_type': 'keg with priming',
            'carbonation_level': 'low',
        }
        self.login(email=self.hidden_user.email)
        rv = self.client.post(self.url, data=data)
        assert rv.status_code == 200
        assert 'Not a valid choice' in rv.text
        assert Brew.query.filter_by(name=data['name']).first() is None


@pytest.mark.usefixtures('client_class')
class TestBrewDeleteView(BrewViewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.brew = brew_factory(
            brewery=self.public_brewery,
            name='pale ale',
            date_brewed=datetime.date.today() - datetime.timedelta(days=30),
            bottling_date=datetime.date.today() - datetime.timedelta(days=10),
        )
        self.url = url_for('brew.delete', brew_id=self.brew.id)

    def test_get_anon(self):
        rv = self.client.get(self.url)
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['Location']

    def test_get_owner(self):
        self.login(email=self.public_user.email)
        rv = self.client.get(self.url)
        assert f'action="{self.url}"' in rv.text

    def test_get_non_owner(self):
        self.login(email=self.hidden_user.email)
        rv = self.client.get(self.url)
        assert rv.status_code == 403

    def test_post_anon(self):
        rv = self.client.post(self.url, data={'delete_it': True})
        assert rv.status_code == 302
        assert url_for('auth.select') in rv.headers['Location']
        assert Brew.query.get(self.brew.id) is not None

    def test_post_owner(self):
        self.login(email=self.public_user.email)
        rv = self.client.post(self.url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 200
        assert Brew.query.get(self.brew.id) is None

    def test_post_non_owner(self):
        self.login(email=self.hidden_user.email)
        rv = self.client.post(self.url, data={'delete_it': True}, follow_redirects=True)
        assert rv.status_code == 403
