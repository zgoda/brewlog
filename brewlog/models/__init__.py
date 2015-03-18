from brewlog.ext import db
from brewlog.models.brewing import Brew, Brewery
from brewlog.models.tasting import TastingNote
from brewlog.models.users import BrewerProfile


def breweries(public_only=True, extra_user=None):
    query = Brewery.query
    if public_only:
        if extra_user:
            query = query.join(BrewerProfile).filter(db.or_(BrewerProfile.is_public==True, BrewerProfile.id==extra_user.id))  # noqa
        else:
            query = query.join(BrewerProfile).filter(BrewerProfile.is_public==True)
    return query


def latest_breweries(ordering, limit=5, public_only=False, extra_user=None):
    return breweries(public_only, extra_user).order_by(db.desc(ordering)).limit(limit).all()


def brews(public_only=True, extra_user=None, user=None):
    query = Brew.query
    if user is not None or public_only:
        query = query.join(Brewery).join(BrewerProfile)
        if user is not None:
            query = query.filter(BrewerProfile.id==user.id)
        if public_only:
            if extra_user is not None:
                query = query.filter(db.or_(BrewerProfile.id==extra_user.id, db.and_(BrewerProfile.is_public==True, Brew.is_public==True)))  # noqa
            else:
                query = query.filter(db.and_(BrewerProfile.is_public==True, Brew.is_public==True))
    return query


def latest_brews(ordering, limit=5, public_only=False, extra_user=None, user=None):
    return brews(public_only, extra_user, user).order_by(db.desc(ordering)).limit(limit)


def tasting_notes(public_only=True, extra_user=None, user=None):
    query = TastingNote.query
    if user is not None:
        query = query.join(BrewerProfile).filter(BrewerProfile.id==user.id)
    if public_only:
        query = query.join(Brew).join(Brewery).join(BrewerProfile)
        if extra_user:
            query = query.filter(db.or_(BrewerProfile.id==extra_user.id, db.and_(BrewerProfile.is_public==True, Brew.is_public==True)))  # noqa
        else:
            query = query.filter(db.and_(BrewerProfile.is_public==True, Brew.is_public==True))
    return query


def latest_tasting_notes(ordering, limit=5, public_only=False, extra_user=None, user=None):
    return tasting_notes(public_only, extra_user, user).order_by(db.desc(ordering)).limit(limit).all()
