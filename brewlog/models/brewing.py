import datetime
import json

import markdown
from flask_babel import lazy_gettext as _
from sqlalchemy_utils import sort_query
from werkzeug.utils import cached_property

from ..ext import db
from ..models import Brewery, choices
from ..utils.brewing import abv, apparent_attenuation, real_attenuation
from ..utils.text import stars2deg


class Brew(db.Model):
    STATE_PLANNED = _('planned')
    STATE_FERMENTING = _('fermenting')
    STATE_FINISHED = _('finished')
    STATE_TAPPED = _('tapped')
    STATE_MATURING = _('maturing')
    __tablename__ = 'brew'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow, index=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20))
    style = db.Column(db.String(200))
    bjcp_style_code = db.Column(db.String(20), default='')
    bjcp_style_name = db.Column(db.String(50), default='')
    bjcp_style = db.Column(db.String(100))
    date_brewed = db.Column(db.Date, index=True)
    notes = db.Column(db.Text)
    notes_html = db.Column(db.Text)
    fermentables = db.Column(db.Text)
    hops = db.Column(db.Text)
    yeast = db.Column(db.Text)
    misc = db.Column(db.Text)
    mash_steps = db.Column(db.Text)
    sparging = db.Column(db.String(200))
    hopping_steps = db.Column(db.Text)
    boil_time = db.Column(db.Integer)
    final_amount = db.Column(db.Float(precision=2))
    bottling_date = db.Column(db.Date)
    carbonation_type = db.Column(db.Enum(*choices.CARBONATION_KEYS, name='carbtype_enum'))
    carbonation_level = db.Column(db.Enum(*choices.CARB_LEVEL_KEYS, name='carblevel_enum'), default='normal')
    carbonation_used = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    is_draft = db.Column(db.Boolean, default=False)
    brewery_id = db.Column(db.Integer, db.ForeignKey('brewery.id'), nullable=False)
    brewery = db.relationship(
        'Brewery',
        backref=db.backref('brews', lazy='dynamic', cascade='all,delete')
    )
    tapped = db.Column(db.Date)
    finished = db.Column(db.Date)

    @cached_property
    def first_step(self):
        return sort_query(self.fermentation_steps, 'date').first()

    @cached_property
    def last_step(self):
        return sort_query(self.fermentation_steps, '-date').first()

    @property
    def og(self):
        if self.first_step:
            return self.first_step.og

    @property
    def fg(self):
        if self.last_step:
            return self.last_step.fg

    @property
    def fermentation_start_date(self):
        if self.first_step:
            return self.first_step.date

    @property
    def brew_length(self):
        if self.first_step:
            return self.first_step.volume

    @property
    def carbonation_data_display(self):
        if self.carbonation_type:
            data = {
                'carb_type': _(dict(choices.CARBONATION_CHOICES)[self.carbonation_type]),
                'carb_level': _(dict(choices.CARB_LEVEL_CHOICES)[self.carbonation_level or 'normal']),
            }
            return _('%(carb_type)s: carbonation %(carb_level)s', **data)
        return ''

    @property
    def is_brewed_yet(self):
        return bool(self.date_brewed and self.date_brewed < datetime.date.today())

    @property
    def attenuation(self):
        if self.og and self.fg:
            return {
                'apparent': apparent_attenuation(self.og, self.fg),
                'real': real_attenuation(self.og, self.fg),
            }
        return {'real': 0, 'apparent': 0}

    def has_access(self, user):
        if self.brewery.brewer != user and not (self.is_public and self.brewery.has_access(user)):
            return False
        return True

    def user_is_brewer(self, user):
        return user in self.brewery.brewers

    def notes_to_json(self):
        notes = {}
        for note in self.tasting_notes:
            notes[f'note_text_{note.id}'] = note.text
        return json.dumps(notes)

    @classmethod
    def get_latest_for(cls, user, public_only=False, limit=None):
        if public_only and not user.is_public:
            return []
        query = cls.query.join(Brewery).filter(Brewery.brewer == user)
        if public_only:
            query = query.filter(Brew.is_public.is_(True))
        query = query.order_by(db.desc(cls.created))
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @property
    def full_name(self):
        parts = []
        if self.code:
            parts.append(f'#{self.code}')
        parts.append(self.name)
        return ' '.join(parts)

    @property
    def abv(self):
        if self.fg and self.og:
            from_carbonation = 0
            if self.carbonation_type.endswith('priming'):
                from_carbonation = choices.CARB_LEVEL_DATA[self.carbonation_level or 'normal']
            return abv(self.og, self.fg, from_carbonation)

    @property
    def current_state(self):
        if not self.date_brewed:
            return (self.STATE_PLANNED, None)  # not brewed yet
        if not self.bottling_date:
            return (self.STATE_FERMENTING, self.date_brewed)  # still in fv
        if self.finished:
            return (self.STATE_FINISHED, self.finished)  # finished
        else:
            if self.tapped:
                return (self.STATE_TAPPED, self.tapped)  # beer is tapped
            else:
                return (self.STATE_MATURING, self.bottling_date)  # beer is maturing

    def get_next(self, public_only=True):
        query = Brew.query
        if public_only:
            query = query.filter(Brew.is_public.is_(True))
        return query.order_by(Brew.id).filter(
            Brew.id > self.id,
            Brew.brewery_id == self.brewery_id
        ).first()

    def get_previous(self, public_only=True):
        query = Brew.query
        if public_only:
            query = query.filter(Brew.is_public.is_(True))
        return query.order_by(db.desc(Brew.id)).filter(
            Brew.id < self.id,
            Brew.brewery_id == self.brewery_id
        ).first()


# events: Brew model
def brew_pre_save(mapper, connection, target):
    style_code = target.bjcp_style_code or ''
    style_name = target.bjcp_style_name or ''
    bjcp_style = f'{style_code} {style_name}'
    bjcp_style = bjcp_style.strip()
    target.bjcp_style = bjcp_style or None
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created


db.event.listen(Brew, 'before_insert', brew_pre_save)
db.event.listen(Brew, 'before_update', brew_pre_save)
