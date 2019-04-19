# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from datetime import date

import pytest


@pytest.mark.usefixtures('app')
class TestBreweryObject:

    def test_established(self, brewery_factory):
        est_date = date(2017, 6, 4)
        brewery = brewery_factory(established_date=est_date)
        assert brewery.est_year == est_date.year
        assert brewery.est_month == est_date.month
        assert brewery.est_day == est_date.day
