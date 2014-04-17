import datetime
import json

import markdown
from flask import url_for
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Date, Float, Enum, Index
from sqlalchemy import event, desc
from sqlalchemy.orm import relationship
from flask.ext.babel import lazy_gettext as _, format_datetime, format_date, gettext

from brewlog.brewing import choices
from brewlog.db import Model
from brewlog.utils.text import slugify, stars2deg
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

    def __unicode__(self):
        return u'<Brewery %s>' % self.name

    @property
    def absolute_url(self):
        return url_for('brewery-details', brewery_id=self.id)

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def other_brewers(self):
        return []

    @property
    def brewers(self):
        return [self.brewer] + self.other_brewers

    @property
    def is_public(self):
        return self.brewer.is_public

    def _brews(self, public_only=False, limit=None, order=None, return_query=False):
        query = Brew.query.filter_by(brewery_id=self.id, is_draft=False)
        if public_only:
            query = query.filter_by(is_public=True)
        if order is not None:
            query = query.order_by(order)
        if limit is not None:
            query = query.limit(limit)
        if return_query:
            return query
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

    def create_brew(self, **kwargs):
        brew = Brew(brewery=self)
        for k, v in kwargs:
            setattr(brew, k, v)
        return brew

    def get_stats(self):
        total_volume = 0
        year_volumes = {}
        year_counts = {}
        for brew in self.brews:
            if brew.final_amount:
                total_volume = total_volume + brew.final_amount
                if brew.date_brewed:
                    year = brew.date_brewed.year
                    amount = year_volumes.setdefault(year, 0)
                    count = year_counts.setdefault(year, 0)
                    year_volumes[year] = amount + brew.final_amount
                    year_counts[year] = count + 1
        return {
            'count_total': self.brews.count(),
            'count_by_year': year_counts,
            'volume_total': total_volume,
            'volume_by_year': year_volumes,
        }

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
    is_last = Column(Boolean, default=False)
    volume = Column(Float(precision=2))
    temperature = Column(Integer)
    notes = Column(Text)
    notes_html = Column(Text)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew')
    __table_args__ = (
        Index('fermentationstep_brew_date', 'brew_id', 'date'),
    )

    def __unicode__(self):
        return u'<FermentationStep %s for %s @%s>' % (self.name, self.brew.name, self.date.strftime('%Y-%m-%d'))

    def previous(self):
        if self.date:
            return FermentationStep.query.filter_by(brew=self.brew).filter(FermentationStep.date < self.date).order_by(desc(FermentationStep.date)).first()

    def next(self):
        if self.date:
            return FermentationStep.query.filter_by(brew=self.brew).filter(FermentationStep.date > self.date).order_by(FermentationStep.date).first()

    @classmethod
    def first_for_brew(cls, brew):
        return cls.query.filter_by(brew=brew).order_by(cls.date).first()

    def step_data(self):
        return {
            'og': self.og or _('unspecified'),
            'fg': self.fg or _('unspecified'), 
            'amount': self.volume or _('unspecified'),
        }

## events: FermentationStep model
def fermentation_step_pre_save(mapper, connection, target):
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    else:
        target.notes_html = None
    next_ = target.next()
    target.is_last = not bool(next_)
    if next_:
        target.fg = next_.og

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
    fermentation_start_date = Column(Date)
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    abv = Column(Float(precision=1))
    brew_length = Column(Float(precision=2))
    fermentation_temperature = Column(Integer)
    final_amount = Column(Float(precision=2))
    bottling_date = Column(Date)
    carbonation_type = Column(Enum(*choices.CARBONATION_KEYS))
    carbonation_level = Column(Enum(*choices.CARB_LEVEL_KEYS), default=u'normal')
    carbonation_used = Column(Text)
    is_public = Column(Boolean, default=True)
    is_draft = Column(Boolean, default=False)
    brewery_id = Column(Integer, ForeignKey('brewery.id'), nullable=False)
    brewery = relationship('Brewery')
    tasting_notes = relationship('TastingNote', cascade='all,delete', lazy='dynamic', order_by='desc(TastingNote.date)')
    fermentation_steps = relationship('FermentationStep', cascade='all,delete', lazy='dynamic')

    def __unicode__(self):
        return u'<Brew %s by %s>' % (self.name, self.brewery.name)

    @property
    def absolute_url(self):
        return url_for('brew-details', brew_id=self.id)

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def render_fields(self):
        return (
            (_('name'), self.name),
            (_('created'), format_datetime(self.created, 'medium')),
            (_('date brewed'), format_date(self.date_brewed, 'medium')),
            (_('style'), self.style),
            (_('BJCP style'), self.bjcp_style),
            (_('brew length'), '%.1f' % self.brew_length),
            (_('original gravity'), '%.1f' % self.og),
            (_('final gravity'), '%.1f' % self.fg),
            (_('abv'), '%.2f' % self.abv),
        )

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
            data['og'] =  '%.1f*Blg' % self.og
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

    def fermentation_step_from_data(self):
        if self.fermentation_start_date:
            fs_data = {
                'name': gettext('primary fermentation'),
                'date': self.fermentation_start_date,
                'og': self.og,
                'brew': self,
                'temperature': self.fermentation_temperature,
                'volume': self.brew_length,
            }
            return FermentationStep(**fs_data)

    @classmethod
    def get_latest_for(cls, user, public_only=False, limit=None):
        query = cls.query.join(Brewery).filter(Brewery.brewer==user)
        if public_only:
            query = query.filter_by(is_public=True)
        if limit is not None:
            query = query.limit(limit)
        return query.order_by(desc(cls.created)).all()

## events: Brew model
def brew_pre_save(mapper, connection, target):
    bjcp_style = u'%s %s' % (target.bjcp_style_code, target.bjcp_style_name)
    target.bjcp_style = bjcp_style.strip()
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created
    if target.og and target.fg and target.carbonation_type and target.carbonation_level:
        from_carbonation = 0
        if target.carbonation_type.endswith(u'priming'):
            from_carbonation = choices.CARB_LEVEL_DATA[target.carbonation_level or u'normal']
        target.abv = abv(target.og, target.fg, from_carbonation)

event.listen(Brew, 'before_insert', brew_pre_save)
event.listen(Brew, 'before_update', brew_pre_save)
