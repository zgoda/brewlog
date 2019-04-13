# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from ..ext import db
from ..models import Brew, BrewerProfile


def public_or_owner(query, user):
    if user is not None:
        query = query.filter(
            db.or_(
                BrewerProfile.id == user.id,
                db.and_(BrewerProfile.is_public.is_(True), Brew.is_public.is_(True))
            )
        )
    else:
        query = query.filter(
            BrewerProfile.is_public.is_(True), Brew.is_public.is_(True)
        )
    return query
