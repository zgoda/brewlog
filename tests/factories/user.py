from factory.alchemy import SQLAlchemyModelFactory

from brewlog.ext import db
from brewlog.models import BrewerProfile


class UserFactory(SQLAlchemyModelFactory):

    class Meta:
        model = BrewerProfile
        session = db.session
