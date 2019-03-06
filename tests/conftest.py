import pytest
from pytest_factoryboy import register

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


@pytest.fixture
def app():
    app = make_app('test')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
