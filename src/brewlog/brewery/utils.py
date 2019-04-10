from flask import abort, jsonify, request, url_for

from ..ext import db
from ..models import BrewerProfile, Brewery


class BreweryUtils:

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
            url = url_for('brewery.details', brewery_id=brewery_id)
            breweries_list.append({'name': name, 'url': url})
        return jsonify(breweries_list)


def check_brewery(brewery_id, user):
    brewery = Brewery.query.get_or_404(brewery_id)
    if not brewery.has_access(user):
        abort(404)
    if request.method == 'POST' and user not in brewery.brewers:
        abort(403)
    return brewery
