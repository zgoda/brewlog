import datetime
from typing import Iterable, Optional

from flask import Response, jsonify, url_for
from flask_babel import gettext, lazy_gettext as _
from flask_sqlalchemy import BaseQuery

from ..ext import db
from ..models import Brew, BrewerProfile, Brewery
from ..models.brewing import BrewState
from ..utils.query import public_or_owner
from ..utils.text import stars2deg


class BrewUtils:

    @staticmethod
    def description(brew: Brew) -> str:
        style = brew.style or brew.bjcp_style or gettext('unspecified style')
        data = [style]
        if brew.abv:
            data.append(gettext('%(abv).1f%% ABV', abv=brew.abv))
        if brew.og:
            data.append(gettext('OG: %(og).1f*Blg', og=brew.og))
        if brew.fg:
            data.append(gettext('FG: %(fg).1f*Blg', fg=brew.fg))
        return stars2deg(', '.join(data))

    @staticmethod
    def display_info(brew: Brew) -> str:
        data = {
            'style': brew.style or brew.bjcp_style or _('not in particular style'),
            'brewery': brew.brewery.name,
            'brewer': brew.brewery.brewer.name,
        }
        return _('%(style)s by %(brewer)s in %(brewery)s', **data)

    @staticmethod
    def fermenting(
                user: Optional[BrewerProfile] = None, public_only: bool = True,
                limit: int = 5
            ) -> Iterable:
        now = datetime.datetime.utcnow()
        query = Brew.query.filter(
            Brew.date_brewed <= now,
            Brew.date_brewed.isnot(None),
            Brew.bottling_date.is_(None),
            Brew.tapped.is_(None),
            Brew.finished.is_(None),
        )
        return BrewUtils._in_state(query, user, public_only, limit)

    @staticmethod
    def maturing(
                user: Optional[BrewerProfile] = None, public_only: bool = True,
                limit: int = 5
            ) -> Iterable:
        now = datetime.datetime.utcnow()
        query = Brew.query.filter(
            Brew.bottling_date <= now,
            Brew.bottling_date.isnot(None),
            Brew.tapped.is_(None),
            Brew.finished.is_(None),
        )
        return BrewUtils._in_state(query, user, public_only, limit)

    @staticmethod
    def on_tap(
                user: Optional[BrewerProfile] = None, public_only: bool = True,
                limit: int = 5
            ) -> Iterable:
        now = datetime.datetime.utcnow()
        query = Brew.query.filter(
            Brew.tapped <= now,
            Brew.tapped.isnot(None),
            Brew.finished.is_(None),
        )
        return BrewUtils._in_state(query, user, public_only, limit)

    @staticmethod
    def latest(
                ordering, limit: int = 5, public_only: bool = False,
                extra_user: Optional[BrewerProfile] = None,
                user: Optional[BrewerProfile] = None, brewed_only: bool = False,
            ) -> BaseQuery:
        query = BrewUtils.brew_list_query(public_only, extra_user, user)
        if brewed_only:
            query = query.filter(Brew.date_brewed.isnot(None))
        return query.order_by(db.desc(ordering)).limit(limit)

    @staticmethod
    def _in_state(
                state_query: BaseQuery, user: Optional[BrewerProfile],
                public_only: bool, limit: int,
            ) -> Iterable:
        if user is not None and (not user.is_public and public_only):
            return []
        query = state_query
        if public_only:
            query = query.filter(Brew.is_public.is_(True))
        if user is not None:
            query = query.join(Brewery).filter(Brewery.brewer == user)
        query = query.order_by(db.desc(Brew.date_brewed))
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def brew_list_query(
                public_only: bool = True, extra_user: Optional[BrewerProfile] = None,
                user: Optional[BrewerProfile] = None,
            ) -> BaseQuery:
        query = Brew.query
        if user is not None or public_only:
            query = query.join(Brewery).join(BrewerProfile)
            if user is not None:
                query = query.filter(BrewerProfile.id == user.id)
            if public_only:
                query = public_or_owner(query, extra_user)
        return query

    @staticmethod
    def brew_search_result(query: BaseQuery) -> Response:
        brew_list = []
        for brew_id, name in query.values(Brew.id, Brew.name):
            url = url_for('brew.details', brew_id=brew_id)
            brew_list.append({'name': name, 'url': url})
        return jsonify(brew_list)

    @staticmethod
    def state_changeable(brew: Brew) -> bool:
        return brew.current_state.name in (
            BrewState.STATE_FINISHED[0], BrewState.STATE_TAPPED[0],
            BrewState.STATE_MATURING[0],
        )


def list_query_for_user(user: BrewerProfile) -> BaseQuery:
    if user.is_anonymous:
        return BrewUtils.brew_list_query()
    return BrewUtils.brew_list_query(public_only=False, user=user)
