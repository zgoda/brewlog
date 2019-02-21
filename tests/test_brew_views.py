import datetime

import pytest
from flask import url_for

from brewlog.models import Brew

from . import BrewlogTests


class BrewViewTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory(first_name='A', last_name='A')
        self.public_brewery = brewery_factory(name='public brewery no. 1', brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False, first_name='B', last_name='B')
        self.hidden_brewery = brewery_factory(name='hidden brewery no. 1', brewer=self.hidden_user)
        self.url = lambda x: url_for('brew.details', brew_id=x.id)


@pytest.mark.usefixtures('client_class')
class TestBrewDetails(BrewViewTests):

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
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
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
        assert Brew.query.get(brew.id).code == data['code']

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

    def test_prefetch_anon(self, brew_factory):
        brew1 = brew_factory(brewery=self.public_brewery, name='pb1')
        brew2 = brew_factory(brewery=self.hidden_brewery, name='hb2')
        rv = self.client.get(url_for('brew.prefetch'))
        data = rv.get_json()
        assert len(data) == 1
        assert data[0]['name'] == brew1.name
        assert data[0]['name'] != brew2.name
