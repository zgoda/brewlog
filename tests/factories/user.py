import factory
from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import BrewerProfile


class UserFactory(SQLAlchemyModelFactory):

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_public = True

    class Meta:
        model = BrewerProfile
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'
