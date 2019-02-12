import pytest

from brewlog.models.brewing import Brew
from brewlog.brew.utils import BrewUtils

from . import BrewlogTests


@pytest.mark.usefixtures('client_class')
class TestBrewUtils(BrewlogTests):

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.brew1 = Brew.query.get(1)
        self.brew2 = Brew.query.get(2)

    def test_brew_description(self):
        utils = BrewUtils(self.brew1)
        ret = utils.brew_description()
        assert 'unspecified style' in ret
        assert 'unknown' in ret

    def test_display_info(self):
        ret = BrewUtils.display_info(self.brew1)
        assert 'not in particular style' in ret
