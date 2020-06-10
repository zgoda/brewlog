from datetime import datetime

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

    def test_emailconfirmation_set(self, mocker, user_factory):
        user = user_factory()
        dt = datetime(2019, 6, 14, 22, 11, 30)
        mocker.patch(
            'brewlog.models.users.datetime',
            mocker.Mock(utcnow=mocker.Mock(return_value=dt)),
        )
        user.set_email_confirmed(True)
        assert user.email_confirmed is True
        assert user.confirmed_dt == dt

    def test_emailconfirmation_clear(self, mocker, user_factory):
        dt = datetime(2019, 6, 14, 22, 11, 30)
        user = user_factory(email_confirmed=True, confirmed_dt=dt)
        user.set_email_confirmed(False)
        assert user.email_confirmed is False
        assert user.confirmed_dt is None
