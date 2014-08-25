from flask.ext.testing import TestCase

from fixture import SQLAlchemyFixture

from brewlog import make_app, db
from brewlog.models.brewing import Brew, Brewery, FermentationStep
from brewlog.models.tasting import TastingNote
from brewlog.models.calendar import Event
from brewlog.models.users import BrewerProfile, CustomLabelTemplate, CustomExportTemplate
from tests.data import BrewData, BreweryData, BrewerProfileData, CustomLabelTemplateData, \
    TastingNoteData, FermentationStepData, CustomExportTemplateData, EventData


class BrewlogTestCase(TestCase):

    def create_app(self):
        app = make_app(env='test')
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.init_db()
        env = {
            'BrewData': Brew,
            'BreweryData': Brewery,
            'BrewerProfileData': BrewerProfile,
            'CustomLabelTemplateData': CustomLabelTemplate,
            'CustomExportTemplateData': CustomExportTemplate,
            'TastingNoteData': TastingNote,
            'FermentationStepData': FermentationStep,
            'EventData': Event,
        }
        fx = SQLAlchemyFixture(env=env, engine=db.engine)
        self.data = fx.data(*[
            BrewData,
            BreweryData,
            BrewerProfileData,
            CustomLabelTemplateData,
            CustomExportTemplateData,
            TastingNoteData,
            FermentationStepData,
            EventData,
        ])
        self.data.setup()

    def tearDown(self):
        self.data.teardown()
        db.session.remove()
        db.clear_db()

    def login(self, client, email=None):
        if email is None:
            email = 'user@example.com'
        return client.get('/auth/local?email=%s' % email, follow_redirects=True)

    def logout(self, client):
        return client.get('/auth/logout', follow_redirects=True)
