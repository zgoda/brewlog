import datetime
import json

import markdown
from flask import url_for
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, Float, Enum, Index
from sqlalchemy import event, desc
from sqlalchemy.orm import relationship
from flask.ext.babel import lazy_gettext as _, format_date, gettext
from werkzeug.utils import cached_property

from brewlog.models import choices
from brewlog.db import Model
from brewlog.utils.text import stars2deg
from brewlog.utils.brewing import abv, aa, ra


class Brewery(Model):
    __tablename__ = 'brewery'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    description_html = Column(Text)
    established_date = Column(Date)
    est_year = Column(Integer)
    est_month = Column(Integer)
    est_day = Column(Integer)
    stats = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow, index=True)
    brewer_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    brewer = relationship('BrewerProfile')
    brews = relationship('Brew', cascade='all,delete', lazy='dynamic')

    def __unicode__(self):  # pragma: no cover
        return u'<Brewery %s>' % self.name

    @property
    def absolute_url(self):
        return url_for('brewery.details', brewery_id=self.id)

    @property
    def other_brewers(self):
        return []

    @property
    def brewers(self):
        return [self.brewer] + self.other_brewers

    def _brews(self, public_only=False, limit=None, order=None):
        query = Brew.query.filter_by(brewery_id=self.id, is_draft=False)
        if public_only:
            query = query.filter_by(is_public=True)
        if order is not None:
            query = query.order_by(order)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def recent_brews(self, public_only=False, limit=10):
        return self._brews(public_only=public_only, limit=limit, order=desc(Brew.created))

    def all_brews(self, public_only=False):
        return self._brews(public_only=public_only, order=desc(Brew.created))

    @property
    def render_fields(self):
        return (
            (_('name'), self.name),
            (_('description'), self.description),
            (_('established'), format_date(self.established_date, 'medium')),
        )

    def has_access(self, user):
        if self.brewer != user:
            if not self.brewer.has_access(user):
                return False
        return True


## events: Brewery model
def brewery_pre_save(mapper, connection, target):
    if target.description:
        target.description_html = markdown.markdown(target.description, safe_mode='remove')
    else:
        target.description_html = None
    if target.updated is None:
        target.updated = target.created
    if target.established_date:
        target.est_year = target.established_date.year
        target.est_month = target.established_date.month
        target.est_day = target.established_date.day

event.listen(Brewery, 'before_insert', brewery_pre_save)
event.listen(Brewery, 'before_update', brewery_pre_save)


class FermentationStep(Model):
    __tablename__ = 'fermentation_step'
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    name = Column(String(200))
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    volume = Column(Float(precision=2))
    temperature = Column(Integer)
    notes = Column(Text)
    notes_html = Column(Text)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew')
    __table_args__ = (
        Index('fermentationstep_brew_date', 'brew_id', 'date'),
    )

    def __unicode__(self):  # pragma: no cover
        return u'<FermentationStep %s for %s @%s>' % (self.name, self.brew.name, self.date.strftime('%Y-%m-%d'))

    def step_data(self):
        return {
            'og': self.og or _('unspecified'),
            'fg': self.fg or _('unspecified'),
            'volume': self.volume or _('unspecified'),
        }

    def previous(self):
        return FermentationStep.query.filter(
            FermentationStep.brew==self.brew, FermentationStep.date<self.date
        ).order_by(desc(FermentationStep.date)).first()

    def next(self):
        return FermentationStep.query.filter(
            FermentationStep.brew==self.brew, FermentationStep.date>self.date
        ).order_by(FermentationStep.date).first()


## events: FermentationStep model
def fermentation_step_pre_save(mapper, connection, target):
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    else:
        target.notes_html = None

event.listen(FermentationStep, 'before_insert', fermentation_step_pre_save)
event.listen(FermentationStep, 'before_update', fermentation_step_pre_save)


class Brew(Model):
    __tablename__ = 'brew'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20))
    style = Column(String(200))
    bjcp_style_code = Column(String(20), default=u'')
    bjcp_style_name = Column(String(50), default=u'')
    bjcp_style = Column(String(100))
    date_brewed = Column(Date, index=True)
    notes = Column(Text)
    notes_html = Column(Text)
    fermentables = Column(Text)
    hops = Column(Text)
    yeast = Column(Text)
    misc = Column(Text)
    mash_steps = Column(Text)
    sparging = Column(String(200))
    hopping_steps = Column(Text)
    boil_time = Column(Integer)
    final_amount = Column(Float(precision=2))
    bottling_date = Column(Date)
    carbonation_type = Column(Enum(*choices.CARBONATION_KEYS, name='carbtype_enum'))
    carbonation_level = Column(Enum(*choices.CARB_LEVEL_KEYS, name='carblevel_enum'), default=u'normal')
    carbonation_used = Column(Text)
    is_public = Column(Boolean, default=True)
    is_draft = Column(Boolean, default=False)
    brewery_id = Column(Integer, ForeignKey('brewery.id'), nullable=False)
    brewery = relationship('Brewery')
    tasting_notes = relationship('TastingNote', cascade='all,delete', lazy='dynamic',
        order_by='desc(TastingNote.date)')
    fermentation_steps = relationship('FermentationStep', cascade='all,delete', lazy='dynamic',
        order_by='asc(FermentationStep.date)')
    events = relationship('Event', cascade='all,delete', lazy='dynamic')

    def __unicode__(self):  # pragma: no cover
        return u'<Brew %s by %s>' % (self.name, self.brewery.name)

    @property
    def absolute_url(self):
        return url_for('brew-details', brew_id=self.id)

    @cached_property
    def first_step(self):
        return FermentationStep.query.filter_by(brew=self).order_by(FermentationStep.date).first()

    @cached_property
    def last_step(self):
        return FermentationStep.query.filter_by(brew=self).order_by(desc(FermentationStep.date)).first()

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
    def display_info(self):
        data = {
            'style': self.style or self.bjcp_style,
            'brewery': self.brewery.name,
            'brewer': self.brewery.brewer.name,
        }
        return _('%(style)s by %(brewer)s in %(brewery)s', **data)

    @property
    def brew_description(self):
        data = {
            'style': self.style or self.bjcp_style or gettext('unspecified style')
        }
        if self.og:
            data['og'] = '%.1f*Blg' % self.og
        else:
            data['og'] = gettext('unknown')
        if self.fg:
            data['fg'] = '%.1f*Blg' % self.fg
        else:
            data['fg'] = gettext('unknown')
        if self.abv:
            data['abv'] = '%.1f%% ABV' % self.abv
        else:
            data['abv'] = gettext('unknown')
        return stars2deg(gettext('%(style)s, %(abv)s, OG: %(og)s, FG: %(fg)s', **data))

    @property
    def carbonation_data_display(self):
        if self.carbonation_type:
            data = {
                'carb_type': _(dict(choices.CARBONATION_CHOICES)[self.carbonation_type]),
                'carb_level': _(dict(choices.CARB_LEVEL_CHOICES)[self.carbonation_level or u'normal']),
            }
            return _('%(carb_type)s: carbonation %(carb_level)s', **data)
        return u''

    @property
    def is_brewed_yet(self):
        return self.date_brewed and self.date_brewed < datetime.date.today()

    @property
    def attenuation(self):
        if self.og and self.fg:
            return {
                'apparent': aa(self.og, self.fg),
                'real': ra(self.og, self.fg),
            }
        return {'real': 0, 'apparent': 0}

    def has_access(self, user):
        if self.brewery.brewer != user:
            if not (self.is_public and self.brewery.has_access(user)):
                return False
        return True

    def notes_to_json(self):
        notes = {}
        for note in self.tasting_notes:
            notes['note_text_%s' % note.id] = note.text
        return json.dumps(notes)

    @classmethod
    def get_latest_for(cls, user, public_only=False, limit=None):
        if public_only and not user.is_public:
            return []
        query = cls.query.join(Brewery).filter(Brewery.brewer==user)
        if public_only:
            query = query.filter(Brew.is_public==True)
        query = query.order_by(desc(cls.created))
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @property
    def full_name(self):
        parts = []
        if self.code:
            parts.append('#%s' % self.code)
        parts.append(self.name)
        return u' '.join(parts)

    @property
    def abv(self):
        if self.fg and self.og:
            from_carbonation = 0
            if self.carbonation_type.endswith('priming'):
                from_carbonation = choices.CARB_LEVEL_DATA[self.carbonation_level or 'normal']
            return abv(self.og, self.fg, from_carbonation)


## events: Brew model
def brew_pre_save(mapper, connection, target):
    bjcp_style = u'%s %s' % (target.bjcp_style_code, target.bjcp_style_name)
    target.bjcp_style = bjcp_style.strip()
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created

event.listen(Brew, 'before_insert', brew_pre_save)
event.listen(Brew, 'before_update', brew_pre_save)
