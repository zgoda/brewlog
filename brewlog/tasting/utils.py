from ..ext import db
from ..models.brewery import Brewery
from ..models.brewing import Brew
from ..models.tasting import TastingNote
from ..models.users import BrewerProfile


class TastingUtils:

    @staticmethod
    def notes(public_only=True, extra_user=None, user=None):
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

    @staticmethod
    def latest_notes(ordering, limit=5, public_only=False, extra_user=None, user=None):
        return TastingUtils.notes(public_only, extra_user, user).order_by(db.desc(ordering)).limit(limit).all()
