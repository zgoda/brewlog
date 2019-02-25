from ..ext import db
from ..models import Brew, BrewerProfile


def public_or_owner(query, user):
    if user is not None:
        query = query.filter(
            db.or_(BrewerProfile.id == user.id,
                db.and_(BrewerProfile.is_public.is_(True), Brew.is_public.is_(True)))
        )
    else:
        query = query.filter(
            BrewerProfile.is_public.is_(True), Brew.is_public.is_(True)
        )
    return query
