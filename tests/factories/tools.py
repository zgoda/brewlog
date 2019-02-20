import factory
from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import CustomExportTemplate, CustomLabelTemplate

from .user import UserFactory


class ExportTemplateFactory(SQLAlchemyModelFactory):

    name = factory.Faker('word')
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = CustomExportTemplate
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class LabelTemplateFactory(SQLAlchemyModelFactory):

    name = factory.Faker('word')
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = CustomLabelTemplate
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
