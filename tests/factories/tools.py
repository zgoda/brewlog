import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Factory as FakerFactory

from brewlog.ext import db
from brewlog.models import CustomExportTemplate, CustomLabelTemplate

from .user import UserFactory

faker = FakerFactory.create()


class ExportTemplateFactory(SQLAlchemyModelFactory):

    name = factory.LazyAttribute(lambda x: faker.sentence(nb_words=2))
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = CustomExportTemplate
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


class LabelTemplateFactory(SQLAlchemyModelFactory):

    name = factory.LazyAttribute(lambda x: faker.sentence(nb_words=2))
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = CustomLabelTemplate
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
