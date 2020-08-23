import datetime
from typing import Iterable, List, Mapping, Optional

from flask_sqlalchemy import BaseQuery

from brewlog.models.fermentation import FermentationStep

from ..ext import db
from ..models import Brew, BrewerProfile, Brewery
from ..models.brewing import BrewState
from ..utils.query import public_or_owner, search_result
from ..utils.text import stars2deg


class BrewUtils:

    @staticmethod
    def description(brew: Brew) -> str:
        style = brew.style or brew.bjcp_style or 'bezstylowiec'
        data = [style]
        if brew.abv:
            data.append(f'alk. {brew.abv}% obj.')
        if brew.og:
            data.append(f'gęstość pocz. {brew.og}*Blg')
        if brew.fg:
            data.append(f'gęstość końcowa {brew.fg}*Blg')
        return stars2deg(', '.join(data))

    @staticmethod
    def display_info(brew: Brew) -> str:
        style = brew.style or brew.bjcp_style or 'bezstylowiec'
        brewery = brew.brewery.name
        brewer = brew.brewery.brewer.name
        return f'{style} przez {brewer} w {brewery}'

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
    def brew_search_result(query: BaseQuery) -> List[Mapping[str, str]]:
        return search_result(query, 'brew.details', 'brew_id')

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


def package_brew(brew: Brew, date: datetime.date, volume: float, fg: float, notes: str):
    step = brew.fermentation_steps.order_by(db.desc(FermentationStep.date)).first()
    if step:
        step.fg = fg
        db.session.add(step)
    brew.final_amount = volume
    brew.bottling_date = date
    brew.carbonation_used = notes
    db.session.add(brew)
    db.session.commit()
