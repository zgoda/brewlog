# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from ..ext import db
from ..models import Brew, BrewerProfile, Brewery, TastingNote
from ..utils.query import public_or_owner


class TastingUtils:

    @staticmethod
    def notes(public_only=True, extra_user=None, user=None):
        query = TastingNote.query
        if user is not None:
            query = query.join(BrewerProfile).filter(BrewerProfile.id == user.id)
        if public_only:
            query = query.join(Brew).join(Brewery).join(BrewerProfile)
            query = public_or_owner(query, extra_user)
        return query

    @staticmethod
    def latest_notes(ordering, limit=5, public_only=False, extra_user=None, user=None):
        return TastingUtils.notes(
            public_only, extra_user, user
        ).order_by(db.desc(ordering)).limit(limit).all()
