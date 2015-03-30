import datetime
import json

import markdown
from flask import url_for
from flask_babelex import lazy_gettext as _, format_date, gettext
from werkzeug.utils import cached_property

from brewlog.ext import db
from brewlog.models import choices
from brewlog.utils.models import DefaultModelMixin
from brewlog.utils.text import stars2deg
from brewlog.utils.brewing import abv, aa, ra


class Brewery(db.Model, DefaultModelMixin):
    __tablename__ = 'brewery'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    established_date = db.Column(db.Date)
    est_year = db.Column(db.Integer)
    est_month = db.Column(db.Integer)
    est_day = db.Column(db.Integer)
    stats = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow, index=True)
    brewer_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    brewer = db.relationship('BrewerProfile')
    brews = db.relationship('Brew', cascade='all,delete', lazy='dynamic')

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
        return query

    def recent_brews(self, public_only=False, limit=10):
        return self._brews(public_only=public_only, limit=limit, order=db.desc(Brew.created))

    def all_brews(self, public_only=False):
        return self._brews(public_only=public_only, order=db.desc(Brew.created))

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


# events: Brewery model
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

db.event.listen(Brewery, 'before_insert', brewery_pre_save)
db.event.listen(Brewery, 'before_update', brewery_pre_save)


class FermentationStep(db.Model, DefaultModelMixin):
    __tablename__ = 'fermentation_step'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, nullable=False)
    name = db.Column(db.String(200))
    og = db.Column(db.Float(precision=1))
    fg = db.Column(db.Float(precision=1))
    volume = db.Column(db.Float(precision=2))
    temperature = db.Column(db.Integer)
    notes = db.Column(db.Text)
    notes_html = db.Column(db.Text)
    brew_id = db.Column(db.Integer, db.ForeignKey('brew.id'), nullable=False)
    brew = db.relationship('Brew')
    __table_args__ = (
        db.Index('fermentationstep_brew_date', 'brew_id', 'date'),
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
        ).order_by(db.desc(FermentationStep.date)).first()

    def next(self):
        return FermentationStep.query.filter(
            FermentationStep.brew==self.brew, FermentationStep.date>self.date
        ).order_by(FermentationStep.date).first()


# events: FermentationStep model
def fermentation_step_pre_save(mapper, connection, target):
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    else:
        target.notes_html = None

db.event.listen(FermentationStep, 'before_insert', fermentation_step_pre_save)
db.event.listen(FermentationStep, 'before_update', fermentation_step_pre_save)


class Brew(db.Model, DefaultModelMixin):
    __tablename__ = 'brew'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow, index=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20))
    style = db.Column(db.String(200))
    bjcp_style_code = db.Column(db.String(20), default=u'')
    bjcp_style_name = db.Column(db.String(50), default=u'')
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
    carbonation_level = db.Column(db.Enum(*choices.CARB_LEVEL_KEYS, name='carblevel_enum'), default=u'normal')
    carbonation_used = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    is_draft = db.Column(db.Boolean, default=False)
    brewery_id = db.Column(db.Integer, db.ForeignKey('brewery.id'), nullable=False)
    brewery = db.relationship('Brewery')
    tasting_notes = db.relationship('TastingNote', cascade='all,delete', lazy='dynamic',
        order_by='desc(TastingNote.date)')
    fermentation_steps = db.relationship('FermentationStep', cascade='all,delete', lazy='dynamic',
        order_by='asc(FermentationStep.date)')
    tapped = db.Column(db.Date)
    finished = db.Column(db.Date)

    def __unicode__(self):  # pragma: no cover
        return u'<Brew %s by %s>' % (self.name, self.brewery.name)

    @property
    def absolute_url(self):
        return url_for('brew.details', brew_id=self.id)

    @cached_property
    def first_step(self):
        return FermentationStep.query.filter_by(brew=self).order_by(FermentationStep.date).first()

    @cached_property
    def last_step(self):
        return FermentationStep.query.filter_by(brew=self).order_by(db.desc(FermentationStep.date)).first()

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
        query = query.order_by(db.desc(cls.created))
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

    @classmethod
    def fermenting(cls, user=None, public_only=True, limit=5):
        if user is not None and (not user.is_public and public_only):
            return []
        now = datetime.datetime.utcnow()
        query = cls.query.filter(Brew.date_brewed<=now, Brew.date_brewed!=None, Brew.bottling_date==None)  # noqa
        if public_only:
            query = query.filter(Brew.is_public==True)
        if user is not None:
            query = query.join(Brewery).filter(Brewery.brewer==user)
        query = query.order_by(db.desc(Brew.date_brewed))
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def maturing(cls, user=None, public_only=True, limit=5):
        if user is not None and (not user.is_public and public_only):
            return []
        now = datetime.datetime.utcnow()
        query = cls.query.filter(Brew.bottling_date<=now, Brew.tapped==None)  # noqa
        if public_only:
            query = query.filter(Brew.is_public==True)
        if user is not None:
            query = query.join(Brewery).filter(Brewery.brewer==user)
        query = query.order_by(db.desc(Brew.date_brewed))
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @classmethod
    def on_tap(cls, user=None, public_only=True, limit=5):
        if user is not None and (not user.is_public and public_only):
            return []
        now = datetime.datetime.utcnow()
        query = cls.query.filter(Brew.tapped<=now, Brew.finished==None)  # noqa
        if public_only:
            query = query.filter(Brew.is_public==True)
        if user is not None:
            query = query.join(Brewery).filter(Brewery.brewer==user)
        query = query.order_by(db.desc(Brew.date_brewed))
        if limit is not None:
            query = query.limit(limit)
        return query.all()


# events: Brew model
def brew_pre_save(mapper, connection, target):
    bjcp_style = u'%s %s' % (target.bjcp_style_code or u'', target.bjcp_style_name or u'')
    bjcp_style = bjcp_style.strip()
    target.bjcp_style = bjcp_style or None
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created

db.event.listen(Brew, 'before_insert', brew_pre_save)
db.event.listen(Brew, 'before_update', brew_pre_save)
