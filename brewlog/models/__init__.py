from sqlalchemy import desc, or_, and_

from brewlog.models.brewing import Brew, Brewery, TastingNote
from brewlog.models.users import BrewerProfile


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

def tasting_notes(public_only=True, extra_user=None):
    query = TastingNote.query
    if public_only:
        query = query.join(Brew).join(Brewery).join(BrewerProfile)
        if extra_user:
            query = query.filter(or_(BrewerProfile.id==extra_user.id, and_(BrewerProfile.is_public==True, Brew.is_public==True)))
        else:
            query = query.filter(and_(BrewerProfile.is_public==True, Brew.is_public==True))
    return query

def latest_tasting_notes(ordering, limit=5, public_only=False, extra_user=None):
    return tasting_notes(public_only, extra_user).order_by(desc(ordering)).limit(limit).all()