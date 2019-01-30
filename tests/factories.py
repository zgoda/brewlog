import factory

from brewlog.ext import db
from brewlog.models.users import BrewerProfile, CustomLabelTemplate


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        sqlalchemy_session = db.session
        model = BrewerProfile


class CustomLabelTemplateFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        sqlalchemy_session = db.session
        model = CustomLabelTemplate
