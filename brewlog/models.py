import datetime

from flask import url_for
from flask_login import UserMixin
from flaskext.babel import lazy_gettext as _, format_datetime, format_date
import markdown
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index, Date, ForeignKey, Float, Enum
from sqlalchemy import event, desc
from sqlalchemy.orm import relationship

from brewlog import Model
from brewlog.brewing import choices
from brewlog.utils.models import DataModelMixin
from brewlog.utils.text import slugify


class BrewerProfile(UserMixin, DataModelMixin, Model):
    __tablename__ = 'brewer_profile'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    nick = Column(String(50))
    email = Column(String(200), index=True, nullable=False)
    full_name = Column(String(100))
    location = Column(String(100))
    about_me = Column(Text)
    is_public = Column(Boolean, default=True)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow, index=True)
    access_token = Column(Text) # for OAuth2
    oauth_token = Column(Text) # for OAuth1a
    oauth_token_secret = Column(Text) # for OAuth1a
    oauth_service = Column(String(50))
    remote_userid = Column(String(100))
    breweries = relationship('Brewery')
    __table_args__ = (
        Index('user_remote_id', 'oauth_service', 'remote_userid'),
    )

    def __unicode__(self):
        return self.email

    def __repr__(self):
        return '<BrewerProfile %s>' % self.email.encode('utf-8')

    @property
    def absolute_url(self):
        return url_for('profile-details', userid=self.id)

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def safe_email(self):
        return self.email.replace('@', '-at-').replace('.', '-dot-')

    @property
    def name(self):
        for attr in ['nick', 'full_name']:
            value = getattr(self, attr, None)
            if value:
                return value
        return _('wanting to stay anonymous')

    @property
    def other_breweries(self):
        return []

    @classmethod
    def last_created(cls, limit=5):
        return cls.query.order_by(desc(cls.created)).limit(limit).all()

    @classmethod
    def last_updated(cls, limit=5):
        return cls.query.order_by(desc(cls.updated)).limit(limit).all()

# mapper events
def profile_pre_save(mapper, connection, target):
    full_name = u'%s %s' % (target.first_name or u'', target.last_name or u'')
    target.full_name = full_name.strip()
    if target.updated is None:
        target.updated = target.created

event.listen(BrewerProfile, 'before_insert', profile_pre_save)
event.listen(BrewerProfile, 'before_update', profile_pre_save)


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
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow, index=True)
    brewer_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    brewer = relationship('BrewerProfile')
    brews = relationship('Brew')

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Brewery %s>' % self.name.encode('utf-8')

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

    def _brews(self, public_only=False, limit=None, order=None, return_query=False):
        query = Brew.query.filter_by(brewery_id=self.id)
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

    @classmethod
    def last_updated(cls, limit=5):
        return cls.query.order_by(desc(cls.updated)).limit(limit).all()

    @classmethod
    def last_created(cls, limit=5):
        return cls.query.order_by(desc(cls.created)).limit(limit).all()

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


class TastingNote(Model):
    __tablename__ = 'tasting_note'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    author = relationship('BrewerProfile')
    date = Column(Date, nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_html = Column(Text)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew')

    def __repr__(self):
        return '<TastingNote by %s for %s>' % (self.author.name.encode('utf-8'), self.brew.name.encode('utf-8'))

## events: TastingNote model
def tasting_note_pre_save(mapper, connection, target):
    if target.text:
        target.text_html = markdown.markdown(target.text, safe_mode='remove')
    else:
        target.text_html = None

event.listen(TastingNote, 'before_insert', tasting_note_pre_save)
event.listen(TastingNote, 'before_update', tasting_note_pre_save)


class AdditionalFermentationStep(Model):
    __tablename__ = 'fermentation_step'
    id = Column(Integer, primary_key=True)
    date = Column(Date, index=True, nullable=False)
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    is_last = Column(Boolean, default=False)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew')

    def __repr__(self):
        return '<AdditionalFermentationStep for %s @%s>' % (self.brew.name, self.date)


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
    fermentation_steps = Column(Text)
    boil_time = Column(Integer)
    fermentation_start_date = Column(Date)
    og = Column(Float(precision=1))
    fg = Column(Float(precision=1))
    brew_length = Column(Float(precision=2))
    fermentation_temperature = Column(Integer)
    final_amount = Column(Float(precision=2))
    bottling_date = Column(Date)
    carbonation_type = Column(Enum(*choices.CARBONATION_KEYS))
    carbonation_used = Column(Text)
    is_public = Column(Boolean, default=True)
    is_draft = Column(Boolean, default=False)
    brewery_id = Column(Integer, ForeignKey('brewery.id'), nullable=False)
    brewery = relationship('Brewery')
    tasting_notes = relationship('TastingNote')
    additional_fermentation_steps = relationship('AdditionalFermentationStep')

    def __repr__(self):
        return '<Brew %s by %s>' % (self.name.encode('utf-8'), self.brewery.name.encode('utf-8'))

    @property
    def absolute_url(self):
        return url_for('brew-details', brew_id=self.id)

    @property
    def slug(self):
        return slugify(self.name)

    @classmethod
    def last_created(cls, limit=5):
        return cls.query.order_by(desc(cls.created)).limit(limit).all()

    @classmethod
    def last_updated(cls, limit=5):
        return cls.query.order_by(desc(cls.updated)).limit(limit).all()

    @property
    def render_fields(self):
        return (
            (_('name'), self.name),
            (_('created'), format_datetime(self.created, 'medium')),
            (_('date brewed'), format_date(self.date_brewed, 'medium')),
            (_('style'), self.style),
            (_('BJCP style'), self.bjcp_style),
            (_('brew length'), self.brew_length),
            (_('original gravity'), self.og),
            (_('final gravity'), self.fg),
        )

    @property
    def display_info(self):
        data = {
            'style': self.style or self.bjcp_style,
            'brewery': self.brewery.name,
            'brewer': self.brewery.brewer.name,
        }
        return _('%(style)s by %(brewer)s in %(brewery)s', **data)

## events: Brew model
def brew_pre_save(mapper, connection, target):
    bjcp_style = u'%s %s' % (target.bjcp_style_code, target.bjcp_style_name)
    target.bjcp_style = bjcp_style.strip()
    target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created

event.listen(Brew, 'before_insert', brew_pre_save)
event.listen(Brew, 'before_update', brew_pre_save)
