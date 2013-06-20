from unittest import TestCase

import brewlog


class BrewlogTestCase(TestCase):

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True

    def setUp(self):
        brewlog.app.config.update(self.__dict__)
        self.client = brewlog.app.test_client()
        brewlog.init_db()
