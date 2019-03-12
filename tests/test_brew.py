import pytest
from flask import url_for

from brewlog.models import Brew, Brewery

from . import BrewlogTests


class BrewTests(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self, brewery_factory, user_factory):
        self.list_url = url_for('brew.all')
        self.create_url = url_for('brew.add')
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(
            brewer=self.public_user, name='public brewery no 1'
        )
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(
            brewer=self.hidden_user, name='hidden brewery no 2'
        )


@pytest.mark.usefixtures('client_class')
class TestBrewNavigation(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )

    def test_next_own_brews(self):
        brew_id = self.public_brewery_public_brew.id
        url = url_for('brew.details', brew_id=brew_id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        next_url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        assert f'<a href="{next_url}">next</a>' in rv.text
        assert '>previous</a>' not in rv.text

    def test_previous_own_brews(self):
        url = url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id)
        self.login(self.public_user.email)
        rv = self.client.get(url)
        prev_url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        assert f'<a href="{prev_url}">previous</a>' in rv.text

    def test_anon_navigation(self):
        """Non-public brews are not accessible in prev/next navigation for
        anonymous user.

        """

        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        rv = self.client.get(url)
        assert url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id) not in rv.text

    def test_non_owner_navigation(self):
        """Non-public brews are not accessible in prev/next navigation for
        non-owners.

        """

        url = url_for('brew.details', brew_id=self.public_brewery_public_brew.id)
        self.login(self.hidden_user.email)
        rv = self.client.get(url)
        assert url_for('brew.details', brew_id=self.public_brewery_hidden_brew.id) not in rv.text


@pytest.mark.usefixtures('app')
class TestBrewObjectLists(BrewTests):

    @pytest.fixture(autouse=True)
    def set_up2(self, brew_factory):
        self.public_brewery_public_brew = brew_factory(
            brewery=self.public_brewery, name='public brew no 1'
        )
        self.public_brewery_hidden_brew = brew_factory(
            brewery=self.public_brewery, is_public=False, name='hidden brew no 1'
        )
        self.hidden_brewery_public_brew = brew_factory(
            brewery=self.hidden_brewery, name='public brew no 2'
        )
        self.hidden_brewery_hidden_brew = brew_factory(
            brewery=self.hidden_brewery, is_public=False, name='hidden brew no 2'
        )

    def test_list_public_only_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=True)]
        hidden_brews = [x.id for x in Brew.query.join(Brewery).filter(
            Brewery.brewer == self.public_user, Brew.is_public.is_(False)
        ).all()]
        for x in hidden_brews:
            assert x not in brew_ids

    def test_list_all_in_public_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=False)]
        assert len(brew_ids) == 2

    def test_list_public_in_hidden_brewery(self):
        brew_ids = [x.id for x in Brew.get_latest_for(self.hidden_user, public_only=True)]
        assert len(brew_ids) == 0

    def test_limit_public_only_in_public_brewery(self):
        limit = 0
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=True, limit=limit)]
        assert len(brew_ids) == limit

    def test_limit_all_in_public_brewery(self):
        limit = 1
        brew_ids = [x.id for x in Brew.get_latest_for(self.public_user, public_only=False, limit=limit)]
        assert len(brew_ids) == limit
