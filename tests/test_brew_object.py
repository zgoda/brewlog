import datetime

import pytest

from brewlog.models import Brew, Brewery
from brewlog.utils.brewing import apparent_attenuation, real_attenuation

from . import BrewlogTests


class BrewObjectTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def _set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(
            brewer=self.public_user, name='public brewery'
        )


@pytest.mark.usefixtures('app')
class TestBrewObject(BrewObjectTests):

    @pytest.mark.parametrize('brewing_date', [
        None,
        datetime.date(2038, 1, 31),
    ], ids=['none', 'in-the-future'])
    def test_is_brewed_not_brewed(self, brewing_date, brew_factory, mocker):
        fake_datetime = mocker.MagicMock()
        fake_datetime.date.today.return_value = datetime.date(2018, 12, 21)
        mocker.patch(
            'brewlog.models.brewing.datetime',
            fake_datetime,
        )
        brew = brew_factory(brewery=self.public_brewery, date_brewed=brewing_date)
        assert brew.is_brewed_yet is False

    def test_is_brewed(self, brew_factory, mocker):
        today = datetime.date(2018, 12, 21)
        fake_datetime = mocker.MagicMock()
        fake_datetime.date.today.return_value = today
        mocker.patch(
            'brewlog.models.brewing.datetime',
            fake_datetime,
        )
        brewing_date = today - datetime.timedelta(days=6)
        brew = brew_factory(brewery=self.public_brewery, date_brewed=brewing_date)
        assert brew.is_brewed_yet is True

    def test_attenuation_og_fg_set(self, brew_factory, fermentation_step_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
        fermentation_step_factory(brew=brew, og=10.5, fg=2.5, name='primary')
        assert brew.attenuation['apparent'] == apparent_attenuation(brew.og, brew.fg)
        assert brew.attenuation['real'] == real_attenuation(brew.og, brew.fg)

    def test_attenuation_no_og_no_fg(self, brew_factory, fermentation_step_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
        fermentation_step_factory(brew=brew, name='primary')
        assert brew.attenuation['apparent'] == 0
        assert brew.attenuation['real'] == 0

    def test_attenuation_og_no_fg(self, brew_factory, fermentation_step_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
        fermentation_step_factory(brew=brew, name='primary', og=10)
        assert brew.attenuation['apparent'] == 0
        assert brew.attenuation['real'] == 0

    def test_notes_formatting(self, brew_factory):
        brew_notes = 'Target: 12*P'
        brew = brew_factory(brewery=self.public_brewery, name='pb1', notes=brew_notes)
        assert '12°P' in brew.notes_html

    @pytest.mark.parametrize('og,fg', [
        (None, None),
        (None, 2.5),
        (10, None)
    ], ids=['no-og-no-fg', 'no-og', 'no-fg'])
    def test_abv_calc_missing_data(
                self, og, fg, brew_factory, fermentation_step_factory
            ):
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
        fermentation_step_factory(brew=brew, name='primary', og=og, fg=fg)
        assert brew.abv is None

    def test_abv_calc_carb_none(self, brew_factory, fermentation_step_factory):
        brew = brew_factory(brewery=self.public_brewery, name='pb1')
        fermentation_step_factory(brew=brew, name='primary', og=10, fg=2.5)
        assert '%.1f' % brew.abv == '3.9'

    @pytest.mark.parametrize('carb_info', [
        None, 'normal'
    ], ids=['none', 'normal'])
    def test_abv_calc_carb_priming_normal(
                self, carb_info, brew_factory, fermentation_step_factory
            ):
        brew = brew_factory(
            brewery=self.public_brewery, name='pb1',
            carbonation_type='keg with priming', carbonation_level=carb_info,
        )
        fermentation_step_factory(brew=brew, name='primary', og=10, fg=2.5)
        assert '%.1f' % brew.abv == '4.2'

    def test_abv_calc_carb_priming_vlow(self, brew_factory, fermentation_step_factory):
        brew = brew_factory(
            brewery=self.public_brewery, name='pb1',
            carbonation_type='keg with priming', carbonation_level='very low',
        )
        fermentation_step_factory(brew=brew, name='primary', og=10, fg=2.5)
        assert '%.1f' % brew.abv == '4.0'


@pytest.mark.usefixtures('app')
class TestBrewObjectLists(BrewObjectTests):

    @pytest.fixture(autouse=True)
    def _set_up2(self, user_factory, brewery_factory, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(
            brewer=self.hidden_user, name='hidden brewery'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

    def test_list_public_only_in_public_brewery(self):
        brew_ids = [
            x.id for x in Brew.get_latest_for(self.public_user, public_only=True)
        ]
        hidden_brews = [x.id for x in Brew.query.join(Brewery).filter(
            Brewery.brewer == self.public_user, Brew.is_public.is_(False)
        ).all()]
        for x in hidden_brews:
            assert x not in brew_ids

    def test_list_all_in_public_brewery(self):
        brew_ids = [
            x.id for x in Brew.get_latest_for(self.public_user, public_only=False)
        ]
        assert len(brew_ids) == 2

    def test_list_public_in_hidden_brewery(self):
        brew_ids = [
            x.id for x in Brew.get_latest_for(self.hidden_user, public_only=True)
        ]
        assert len(brew_ids) == 0

    def test_limit_public_only_in_public_brewery(self):
        limit = 0
        brew_ids = [
            x.id for x in Brew.get_latest_for(
                self.public_user, public_only=True, limit=limit
            )
        ]
        assert len(brew_ids) == limit

    def test_limit_all_in_public_brewery(self):
        limit = 1
        brew_ids = [
            x.id for x in Brew.get_latest_for(
                self.public_user, public_only=False, limit=limit
            )
        ]
        assert len(brew_ids) == limit
