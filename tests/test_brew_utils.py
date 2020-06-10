from datetime import date, timedelta

import pytest

from brewlog.brew.utils import BrewUtils


@pytest.mark.usefixtures('app')
class TestBrewUtils:

    @pytest.fixture(autouse=True)
    def set_up(self, brew_factory):
        self.brew1 = brew_factory()
        self.brew2 = brew_factory()

    def test_brew_description(self):
        ret = BrewUtils.description(self.brew1)
        assert ret == 'unspecified style'

    def test_display_info(self):
        ret = BrewUtils.display_info(self.brew1)
        assert 'not in particular style' in ret


@pytest.mark.usefixtures('app')
class TestBrewUtilsStateFermenting:

    @pytest.fixture(autouse=True)
    def set_up(self, brew_factory, user_factory):
        today = date.today()
        self.brew_1 = brew_factory(
            name='fermenting 1',
            date_brewed=today - timedelta(days=7),
        )
        self.brew_2 = brew_factory(
            name='fermenting 2',
            date_brewed=today - timedelta(days=9),
        )
        self.brew_3 = brew_factory(
            name='fermenting 3 (hidden)',
            date_brewed=today - timedelta(days=12),
            is_public=False,
        )
        self.hidden_user = user_factory(is_public=False)

    def test_public_only(self):
        ret = BrewUtils.fermenting()
        assert len(ret) == 2

    def test_public_only_with_limit(self):
        limit = 1
        ret = BrewUtils.fermenting(limit=limit)
        assert len(ret) == limit

    def test_public_only_for_public_user(self):
        ret = BrewUtils.fermenting(user=self.brew_3.brewery.brewer)
        assert len(ret) == 0

    def test_public_only_for_hidden_user(self, brewery_factory, brew_factory):
        date_brewed = date.today() - timedelta(days=4)
        brewery = brewery_factory(name='hidden brewery', brewer=self.hidden_user)
        brew_factory(name='hidden 1', brewery=brewery, date_brewed=date_brewed)
        brew_factory(name='hidden 2', brewery=brewery, date_brewed=date_brewed)
        ret = BrewUtils.fermenting(user=self.hidden_user, public_only=True)
        assert len(ret) == 0

    def test_all(self):
        ret = BrewUtils.fermenting(public_only=False)
        assert len(ret) == 3

    def test_all_with_limit(self):
        limit = 2
        ret = BrewUtils.fermenting(public_only=False, limit=limit)
        assert len(ret) == limit

    def test_all_for_public_user(self, brew_factory):
        extra_brew = brew_factory(
            name='extra brew',
            date_brewed=date.today() - timedelta(days=2),
            brewery=self.brew_3.brewery
        )
        ret = BrewUtils.fermenting(user=extra_brew.brewery.brewer, public_only=False)
        assert len(ret) == 2

    def test_all_for_hidden_user(self, brewery_factory, brew_factory):
        date_brewed = date.today() - timedelta(days=4)
        brewery = brewery_factory(name='hidden brewery', brewer=self.hidden_user)
        brew_factory(name='hidden 1', brewery=brewery, date_brewed=date_brewed)
        brew_factory(name='hidden 2', brewery=brewery, date_brewed=date_brewed)
        ret = BrewUtils.fermenting(user=self.hidden_user, public_only=False)
        assert len(ret) == 2


@pytest.mark.usefixtures('app')
class TestBrewListQuery:

    def test_anon_only_public(self, user_factory, brewery_factory, brew_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner)
        brew_1 = brew_factory(brewery=brewery, is_public=True)
        brew_2 = brew_factory(brewery=brewery, is_public=False)
        q = BrewUtils.brew_list_query().all()
        assert brew_1 in q
        assert brew_2 not in q

    def test_anon_all(self, user_factory, brewery_factory, brew_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner)
        brew_1 = brew_factory(brewery=brewery, is_public=True)
        brew_2 = brew_factory(brewery=brewery, is_public=False)
        q = BrewUtils.brew_list_query(public_only=False).all()
        assert brew_1 in q
        assert brew_2 in q

    def test_owner_all(self, user_factory, brewery_factory, brew_factory):
        owner = user_factory(is_public=True)
        brewery = brewery_factory(brewer=owner)
        brew_1 = brew_factory(brewery=brewery, is_public=True)
        brew_2 = brew_factory(brewery=brewery, is_public=False)
        q = BrewUtils.brew_list_query(extra_user=owner).all()
        assert brew_1 in q
        assert brew_2 in q
