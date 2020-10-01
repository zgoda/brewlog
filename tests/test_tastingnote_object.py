import datetime

import pytest

from brewlog.models import TastingNote


@pytest.mark.usefixtures('app')
class TestTastingNoteObject:

    @pytest.fixture(autouse=True)
    def _set_up(self, user_factory, brewery_factory):
        self.public_user = user_factory()
        self.public_brewery = brewery_factory(brewer=self.public_user)
        self.hidden_user = user_factory(is_public=False)
        self.hidden_brewery = brewery_factory(brewer=self.hidden_user)

    def test_create_with_date(self, user_factory, brew_factory):
        brew = brew_factory(brewery=self.public_brewery)
        date = datetime.date(year=1992, month=12, day=4)
        user = user_factory()
        text = 'note X'
        note = TastingNote.create_for(
            brew, author=user, text=text, date=date
        )
        assert note.date == date

    def test_create_no_date(self, user_factory, brew_factory, mocker):
        brew = brew_factory(brewery=self.public_brewery)
        date = datetime.date(year=1992, month=12, day=4)
        fake_datetime = mocker.MagicMock()
        fake_datetime.date.today.return_value = date
        mocker.patch(
            'brewlog.models.tasting.datetime',
            fake_datetime,
        )
        user = user_factory()
        text = 'note X'
        note = TastingNote.create_for(
            brew, author=user, text=text,
        )
        assert note.date == date
