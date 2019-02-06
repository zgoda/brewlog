import pytest
from fixture import SQLAlchemyFixture

from brewlog import make_app
from brewlog.ext import db
from brewlog.models.brewing import Brew, Brewery, FermentationStep
from brewlog.models.tasting import TastingNote
from brewlog.models.users import (
    BrewerProfile, CustomExportTemplate, CustomLabelTemplate
)

from . import fixtures


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
