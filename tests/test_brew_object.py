import datetime

import pytest

from . import BrewlogTests


class BrewObjectTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user, name='public brewery no. 1')
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user, name='hidden brewery no. 1')


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
