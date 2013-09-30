from sqlalchemy import desc, or_, and_

from brewlog.models.brewing import Brew, Brewery
from brewlog.models.users import BrewerProfile


def latest_brews_for(user):
    query = Brew.query.join(Brewery).join(BrewerProfile).filter(BrewerProfile.id==user.id).order_by(desc(Brew.created))
    return query.all()

def breweries(public_only=True, extra_user=None):
    query = Brewery.query
    if public_only:
        if extra_user:
            query = query.join(BrewerProfile).filter(or_(BrewerProfile.is_public==True, BrewerProfile.id==extra_user.id))
        else:
            query = query.join(BrewerProfile).filter(BrewerProfile.is_public==True)
    return query

def latest_breweries(ordering, limit=5, public_only=False, extra_user=None):
    return breweries(public_only, extra_user).order_by(desc(ordering)).limit(limit).all()

def brews(public_only=True, extra_user=None):
    query = Brew.query
    if public_only:
        query = query.join(Brewery).join(BrewerProfile)
        if extra_user:
            query = query.filter(or_(BrewerProfile.id==extra_user.id, and_(BrewerProfile.is_public==True, Brew.is_public==True)))
        else:
            query = query.filter(and_(BrewerProfile.is_public==True, Brew.is_public==True))
    return query

def latest_brews(ordering, limit=5, public_only=False, extra_user=None):
    return brews(public_only, extra_user).order_by(desc(ordering)).limit(limit).all()