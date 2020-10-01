import pytest
from flask.wrappers import Response
from pytest_factoryboy import register
from werkzeug.utils import cached_property

from brewlog import make_app
from brewlog.ext import db

from .factories import (
    BreweryFactory, BrewFactory, FermentationStepFactory, TastingNoteFactory,
    UserFactory,
)

register(UserFactory)
register(BreweryFactory)
register(BrewFactory)
register(FermentationStepFactory)
register(TastingNoteFactory)


class BrewlogTestResponse(Response):

    @cached_property
    def text(self):
        if self.mimetype.startswith('text'):
            return self.data.decode(self.charset)
        return self.data


@pytest.fixture(scope='session')
def _environ(monkeypatch, tmp_path):
    monkeypatch.setenv('MAILGUN_DOMAIN', 'some-domain.somewhere.net')
    monkeypatch.setenv('MAILGUN_API_KEY', 'some-key')
    monkeypatch.setenv('INSTANCE_PATH', str(tmp_path / 'instance'))


@pytest.fixture()
def app():
    app = make_app('test')
    app.response_class = BrewlogTestResponse
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
