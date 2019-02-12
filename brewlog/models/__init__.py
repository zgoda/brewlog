from ..ext import db
from .brewing import Brew, Brewery
from .tasting import TastingNote
from .users import BrewerProfile

from . import dbtrigger  # noqa


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


def latest_breweries(ordering, limit=5, public_only=False, extra_user=None):
    return breweries(public_only, extra_user).order_by(db.desc(ordering)).limit(limit).all()


def tasting_notes(public_only=True, extra_user=None, user=None):
    query = TastingNote.query
    if user is not None:
        query = query.join(BrewerProfile).filter(BrewerProfile.id == user.id)
    if public_only:
        query = query.join(Brew).join(Brewery).join(BrewerProfile)
        if extra_user:
            query = query.filter(
                db.or_(BrewerProfile.id == extra_user.id,
                    db.and_(BrewerProfile.is_public.is_(True), Brew.is_public.is_(True)))
            )
        else:
            query = query.filter(
                db.and_(BrewerProfile.is_public.is_(True), Brew.is_public.is_(True))
            )
    return query


def latest_tasting_notes(ordering, limit=5, public_only=False, extra_user=None, user=None):
    return tasting_notes(public_only, extra_user, user).order_by(db.desc(ordering)).limit(limit).all()
