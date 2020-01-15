from flask import url_for

from ..ext import db
from ..models import Brew, BrewerProfile, Brewery


class BreweryUtils:

    def __init__(self, brewery):
        self.brewery = brewery

    @staticmethod
    def breweries(public_only=True, extra_user=None):
        query = Brewery.query
        if public_only:
            if extra_user:
                query = query.join(BrewerProfile).filter(
                    db.or_(
                        BrewerProfile.is_public.is_(True), Brewery.brewer == extra_user
                    )
                )
            else:
                query = query.join(
                    BrewerProfile
                ).filter(BrewerProfile.is_public.is_(True))
        return query

    @staticmethod
    def latest_breweries(ordering, limit=5, public_only=False, extra_user=None):
        return BreweryUtils.breweries(
            public_only, extra_user
        ).order_by(db.desc(ordering)).limit(limit).all()

    @staticmethod
    def brewery_search_result(query):
        breweries_list = []
        for brewery_id, name in query.values(Brewery.id, Brewery.name):
            breweries_list.append(
                {'name': name, 'url': url_for('brewery.details', brewery_id=brewery_id)}
            )
        return breweries_list

    @staticmethod
    def brews(brewery, order, public_only=True, limit=None):
        query = brewery.brews.filter_by(is_draft=False)
        if public_only:
            query = query.filter_by(is_public=True)
        query = query.order_by(order)
        if limit is not None:
            query = query.limit(limit)
        return query

    def recent_brews(self, public_only=True, limit=10):
        return self.brews(
            self.brewery, order=db.desc(Brew.created), public_only=public_only,
            limit=limit,
        )
