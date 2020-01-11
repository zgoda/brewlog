import datetime

import factory
from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import Brew, Brewery, FermentationStep, TastingNote

from .user import UserFactory


class BreweryFactory(SQLAlchemyModelFactory):

    name = factory.Faker('word')
    brewer = factory.SubFactory(UserFactory)
    established_date = factory.Faker('date_this_decade')
    description = factory.Faker('paragraph')

    class Meta:
        model = Brewery
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'


class BrewFactory(SQLAlchemyModelFactory):

    name = factory.Faker('word')
    brewery = factory.SubFactory(BreweryFactory)
    is_public = True
    is_draft = False

    class Meta:
        model = Brew
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'


class FermentationStepFactory(SQLAlchemyModelFactory):

    date = factory.LazyFunction(datetime.datetime.utcnow)
    name = factory.Faker('word')
    brew = factory.SubFactory(BrewFactory)

    class Meta:
        model = FermentationStep
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'


class TastingNoteFactory(SQLAlchemyModelFactory):

    date = factory.LazyFunction(datetime.datetime.utcnow)
    author = factory.SubFactory(UserFactory)
    brew = factory.SubFactory(BrewFactory)
    text = factory.Faker('paragraph')

    class Meta:
        model = TastingNote
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'flush'
