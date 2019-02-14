from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import Brewery, Brew, FermentationStep, TastingNote


class BreweryFactory(SQLAlchemyModelFactory):

    class Meta:
        model = Brewery
        session = db.session


class BrewFactory(SQLAlchemyModelFactory):

    class Meta:
        model = Brew
        session = db.session


class FermentationStepFactory(SQLAlchemyModelFactory):

    class Meta:
        model = FermentationStep
        session = db.session


class TastingNoteFactory(SQLAlchemyModelFactory):

    class Meta:
        model = TastingNote
        session = db.session
