from ..ext import db
from ..models.users import BrewerProfile
from ..models.brewery import Brewery


class BreweryUtils:

    @staticmethod
    def breweries(public_only=True, extra_user=None):
        query = Brewery.query
        if public_only:
            if extra_user:
                query = query.join(BrewerProfile).filter(
                    db.or_(BrewerProfile.is_public.is_(True), BrewerProfile.id == extra_user.id)
                )
            else:
                query = query.join(BrewerProfile).filter(BrewerProfile.is_public.is_(True))
        return query

    @staticmethod
    def latest_breweries(ordering, limit=5, public_only=False, extra_user=None):
        return BreweryUtils.breweries(public_only, extra_user).order_by(db.desc(ordering)).limit(limit).all()
