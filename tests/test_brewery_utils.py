# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import pytest

from brewlog.brewery.utils import BreweryUtils


@pytest.mark.usefixtures('app')
class TestBreweryUtils:

    @pytest.fixture(autouse=True)
    def set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(
            brewer=self.public_user, name='public brewery no 1'
        )
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(
            brewer=self.hidden_user, name='hidden brewery no 1'
        )

    def test_breweries_public_only(self):
        query = BreweryUtils.breweries()
        assert query.count() == 1

    def test_breweries_public_only_extra_user(self):
        query = BreweryUtils.breweries(extra_user=self.hidden_user)
        assert query.count() == 2

    def test_breweries_all(self):
        query = BreweryUtils.breweries(public_only=False)
        assert query.count() == 2
