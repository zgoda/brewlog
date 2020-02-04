from datetime import datetime

import factory
from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import Brew, BrewerProfile, Brewery, FermentationStep, TastingNote


class BaseFactory(SQLAlchemyModelFactory):

    class Meta:
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'


class UserFactory(BaseFactory):

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_public = True
    password = factory.PostGenerationMethodCall('set_password', 'password')

    class Meta:
        model = BrewerProfile


class BreweryFactory(BaseFactory):

    name = factory.Faker('word')
    brewer = factory.SubFactory(UserFactory)
    established_date = factory.Faker('date_this_decade')
    description = factory.Faker('paragraph')

    class Meta:
        model = Brewery


class BrewFactory(BaseFactory):

    name = factory.Faker('word')
    brewery = factory.SubFactory(BreweryFactory)
    is_public = True
    is_draft = False

    class Meta:
        model = Brew


class FermentationStepFactory(BaseFactory):

    date = factory.LazyFunction(datetime.utcnow)
    name = factory.Faker('word')
    brew = factory.SubFactory(BrewFactory)

    class Meta:
        model = FermentationStep


class TastingNoteFactory(BaseFactory):

    date = factory.LazyFunction(datetime.utcnow)
    author = factory.SubFactory(UserFactory)
    brew = factory.SubFactory(BrewFactory)
    text = factory.Faker('paragraph')

    class Meta:
        model = TastingNote
