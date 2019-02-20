import pytest

from brewlog.brew.utils import BrewUtils
from brewlog.models import Brew


@pytest.mark.usefixtures('client_class')
class TestBrewUtils:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.brew1 = Brew.query.get(1)
        self.brew2 = Brew.query.get(2)

    def test_brew_description(self):
        ret = BrewUtils.description(self.brew1)
        assert 'unspecified style' in ret
        assert 'unknown' in ret

    def test_display_info(self):
        ret = BrewUtils.display_info(self.brew1)
        assert 'not in particular style' in ret
