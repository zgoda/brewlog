import pytest
from fixture import SQLAlchemyFixture
from pytest_factoryboy import register

from brewlog import make_app
from brewlog.ext import db
from brewlog.models import (
    Brew, BrewerProfile, Brewery, CustomExportTemplate, CustomLabelTemplate,
    FermentationStep, TastingNote
)

from . import fixtures
from .factories import (
    BreweryFactory, BrewFactory, ExportTemplateFactory,
    FermentationStepFactory, LabelTemplateFactory, TastingNoteFactory,
    UserFactory
)

register(UserFactory)
register(ExportTemplateFactory)
register(LabelTemplateFactory)
register(BreweryFactory)
register(BrewFactory)
register(FermentationStepFactory)
register(TastingNoteFactory)


@pytest.fixture
def app():
    app = make_app('test')
    with app.app_context():
        db.create_all()
        env = {
            'BrewData': Brew,
            'BreweryData': Brewery,
            'BrewerProfileData': BrewerProfile,
            'CustomLabelTemplateData': CustomLabelTemplate,
            'CustomExportTemplateData': CustomExportTemplate,
            'TastingNoteData': TastingNote,
            'FermentationStepData': FermentationStep,
        }
        fx = SQLAlchemyFixture(env=env, engine=db.engine)
        data = fx.data(*[
            fixtures.BrewData,
            fixtures.BreweryData,
            fixtures.BrewerProfileData,
            fixtures.CustomLabelTemplateData,
            fixtures.CustomExportTemplateData,
            fixtures.TastingNoteData,
            fixtures.FermentationStepData,
        ])
        data.setup()
        yield app
        data.teardown()
        db.session.remove()
        db.drop_all()
