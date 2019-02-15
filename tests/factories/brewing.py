import factory
from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import Brew, Brewery, FermentationStep, TastingNote
from .user import UserFactory


class BreweryFactory(SQLAlchemyModelFactory):

    name = factory.Faker('word')
    brewer = factory.SubFactory(UserFactory)

    class Meta:
        model = Brewery
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class BrewFactory(SQLAlchemyModelFactory):

    class Meta:
        model = Brew
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class FermentationStepFactory(SQLAlchemyModelFactory):

    class Meta:
        model = FermentationStep
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class TastingNoteFactory(SQLAlchemyModelFactory):

    class Meta:
        model = TastingNote
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
