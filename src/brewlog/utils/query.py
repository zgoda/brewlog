from flask import url_for

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


def search_result(query, endpoint, attr_name):
    res = []
    id_col = query.column_descriptions[0]['entity'].id
    name_col = query.column_descriptions[0]['entity'].name
    for obj_id, obj_name in query.values(id_col, name_col):
        kw = {attr_name: obj_id}
        res.append({'name': obj_name, 'url': url_for(endpoint, **kw)})
    return res
