import pytest

from brewlog.models import BrewerProfile


@pytest.mark.usefixtures('app')
class TestBrewerProfileObject:

    def test_create_no_names(self, user_factory):
        user = user_factory(first_name=None, last_name=None, nick=None)
        assert 'anonymous' in user.name.lower()

    def test_last_created_public_only(self, user_factory):
        user_factory(is_public=True)
        user_factory(is_public=False)
        assert len(BrewerProfile.last_created(public_only=True)) == 1

    def test_last_created_all(self, user_factory):
        user_factory(is_public=True)
        user_factory(is_public=False)
        assert len(BrewerProfile.last_created(public_only=False)) == 2

    def test_public_ordering(self, user_factory):
        user_p_b = user_factory(nick='b', is_public=True)
        user_p_a = user_factory(nick='a', is_public=True)
        assert BrewerProfile.public(order_by=BrewerProfile.nick).first() == user_p_a
        assert BrewerProfile.public().first() == user_p_b
