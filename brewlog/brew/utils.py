import datetime

from flask_babel import lazy_gettext as gettext

from ..ext import db
from ..models.brewing import Brew
from ..models.brewery import Brewery
from ..utils.text import stars2deg


class BrewUtils:

    def __init__(self, brew):
        self.brew = brew

    def brew_description(self):
        data = {
            'style': self.brew.style or self.brew.bjcp_style or gettext('unspecified style')
        }
        data['og'] = '%.1f*Blg' % self.brew.og if self.brew.og else gettext('unknown')
        data['fg'] = '%.1f*Blg' % self.brew.fg if self.brew.fg else gettext('unknown')
        data['abv'] = '%.1f%% ABV' % self.brew.abv if self.brew.abv else gettext('unknown')
        return stars2deg(gettext('%(style)s, %(abv)s, OG: %(og)s, FG: %(fg)s', **data))

    @staticmethod
    def fermenting(user=None, public_only=True, limit=5):
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
    def maturing(user=None, public_only=True, limit=5):
        now = datetime.datetime.utcnow()
        query = Brew.query.filter(
            Brew.bottling_date <= now,
            Brew.bottling_date.isnot(None),
            Brew.tapped.is_(None),
            Brew.finished.is_(None),
        )
        return BrewUtils._in_state(query, user, public_only, limit)

    @staticmethod
    def on_tap(user=None, public_only=True, limit=5):
        now = datetime.datetime.utcnow()
        query = Brew.query.filter(
            Brew.tapped <= now,
            Brew.tapped.isnot(None),
            Brew.finished.is_(None),
        )
        return BrewUtils._in_state(query, user, public_only, limit)

    @staticmethod
    def _in_state(state_query, user, public_only, limit):
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
