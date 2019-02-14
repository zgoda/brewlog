from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import CustomExportTemplate, CustomLabelTemplate


class ExportTemplateFactory(SQLAlchemyModelFactory):

    class Meta:
        model = CustomExportTemplate
        session = db.session


class LabelTemplateFactory(SQLAlchemyModelFactory):

    class Meta:
        model = CustomLabelTemplate
        session = db.session
