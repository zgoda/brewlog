import pytest
from wtforms.validators import ValidationError

from brewlog.forms.validators import Email


class TestEmailValidator:

    def test_default_message(self, mocker):
        fake_field = mocker.Mock(data='invalid')
        v = Email()
        with pytest.raises(ValidationError) as exc:
            v(None, fake_field)
            assert 'not a valid email address' in str(exc.data)

    def test_custom_message(self, mocker):
        fake_field = mocker.Mock(data='invalid')
        msg = 'data invalid'
        v = Email(msg)
        with pytest.raises(ValidationError) as exc:
            v(None, fake_field)
            assert msg in str(exc.data)
