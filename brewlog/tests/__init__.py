from flask import Flask
from flask.ext.testing import TestCase

from brewlog import app, session, init_db, clear_db


class BrewlogTestCase(TestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def create_app(self):
        self.app = app
        self.app.config.update(self.__dict__)
        return app

    def setUp(self):
        init_db()

    def tearDown(self):
        session.remove()
        clear_db()
