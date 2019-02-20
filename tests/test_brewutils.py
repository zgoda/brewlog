import pytest

from brewlog.brew.utils import BrewUtils


@pytest.mark.usefixtures('client_class')
class TestBrewUtils:

    @pytest.fixture(autouse=True)
    def set_up(self, brew_factory):
        self.brew1 = brew_factory()
        self.brew2 = brew_factory()

    def test_brew_description(self):
        ret = BrewUtils.description(self.brew1)
        assert 'unspecified style' in ret
        assert 'unknown' in ret

    def test_display_info(self):
        ret = BrewUtils.display_info(self.brew1)
        assert 'not in particular style' in ret
