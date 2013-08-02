from flask_testing import TestCase

from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

from brewlog import make_app, db, models
from brewlog.tests.data import BrewData


class BrewlogTestCase(TestCase):

    def create_app(self):
        app = make_app(env='test')
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.init_db()
        fx = SQLAlchemyFixture(env=models, style=NamedDataStyle(), engine=db.engine)
        self.data = fx.data(BrewData)
        self.data.setup()

    def tearDown(self):
        self.data.teardown()
        db.session.remove()
        db.clear_db()
