import datetime

from flask import url_for
from flask_login import UserMixin
from flask_babel import lazy_gettext as _, format_datetime, format_date
import markdown
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index, Date, ForeignKey, Float, Enum
from sqlalchemy import event, desc, or_, and_
from sqlalchemy.orm import relationship

from brewlog.db import Model
from brewlog.brewing import choices
from brewlog.utils.models import DataModelMixin
from brewlog.utils.text import slugify, stars2deg
from brewlog.utils.dataimport import import_beerxml
from brewlog.utils.brewing import abv


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
    ipboard_setups = relationship('IPBoardExportSetup')
    custom_export_templates = relationship('CustomExportTemplate')
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
    def breweries_list_url(self):
        return url_for('profile-breweries', userid=self.id)

    @property
    def brews_list_url(self):
        return url_for('profile-brews', userid=self.id)

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
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def _last(cls, ordering, public_only=False, limit=5, extra_user=None):
        query = cls.query
        if public_only:
            if extra_user:
                query = query.filter(or_(cls.is_public==True, cls.id==extra_user.id))
            else:
                query = query.filter_by(is_public=True)
        return query.order_by(desc(ordering)).limit(limit).all()

    @classmethod
    def last_created(cls, public_only=False, limit=5, **kwargs):
        extra_user = kwargs.get('extra_user', None)
        return cls._last(cls.created, public_only, limit, extra_user)

    @classmethod
    def last_updated(cls, public_only=False, limit=5, **kwargs):
        extra_user = kwargs.get('extra_user', None)
        return cls._last(cls.updated, public_only, limit, extra_user)

    @property
    def latest_brews(self):
        query = Brew.query.join(Brewery).join(BrewerProfile).filter(BrewerProfile.id==self.id).order_by(desc(Brew.created))
        return query.all()

    @property
    def ipb_export_setups(self, active_only=False):
        query = IPBoardExportSetup.query.join(BrewerProfile).filter(BrewerProfile.id==self.id)
        if active_only:
            query = query.filter_by(is_active=True)
        query.order_by(IPBoardExportSetup.service_name)
        return query.all()

    def has_access(self, user):
        if self != user:
            if not self.is_public:
                return False
        return True

# mapper events
def profile_pre_save(mapper, connection, target):
    full_name = u'%s %s' % (target.first_name or u'', target.last_name or u'')
    target.full_name = full_name.strip()
    if target.updated is None:
        target.updated = target.created

event.listen(BrewerProfile, 'before_insert', profile_pre_save)
event.listen(BrewerProfile, 'before_update', profile_pre_save)


class IPBoardExportSetup(Model):
    __tablename__ = 'ipboard_export_setup'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    user = relationship('BrewerProfile')
    service_name = Column(String(50), nullable=False)
    topic_id = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    __table_args__ = (
        Index('ipb_user_service', 'user_id', 'service_name'),
    )


class CustomExportTemplate(Model):
    __tablename__ = 'custom_export_template'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    user = relationship('BrewerProfile')
    name = Column(String(100), nullable=False)
    text = Column(Text)
    __table__args__ = (
        Index('user_export_template', 'user_id', 'name'),
    )


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

    @classmethod
    def _last(cls, ordering, limit=5, public_only=False, extra_user=None):
        return cls.public_query().order_by(desc(ordering)).limit(limit).all()

    @classmethod
    def last_updated(cls, limit=5, public_only=False, **kwargs):
        extra_user = kwargs.get('extra_user')
        return cls._last(cls.updated, limit, public_only, extra_user)

    @classmethod
    def last_created(cls, limit=5, public_only=False, **kwargs):
        extra_user = kwargs.get('extra_user')
        return cls._last(cls.created, limit, public_only, extra_user)

    @classmethod
    def public_query(cls, public_only=True, extra_user=None):
        query = cls.query
        if public_only:
            if extra_user:
                query = query.join(BrewerProfile).filter(or_(BrewerProfile.is_public==True, BrewerProfile.id==extra_user.id))
            else:
                query = query.join(BrewerProfile).filter(BrewerProfile.is_public==True)
        return query

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

    def import_recipes_from(self, source, filetype, save=True):
        if filetype.lower() == 'beerxml':
            brews, num_failed = import_beerxml(source, self, save)
        return len(brews), num_failed

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
    def public_query(cls, public_only=True, extra_user=None):
        query = cls.query
        if public_only:
            query = query.join(Brewery).join(BrewerProfile)
            if extra_user:
                query = query.filter(or_(BrewerProfile.id==extra_user.id, and_(BrewerProfile.is_public==True, cls.is_public==True)))
            else:
                query = query.filter(and_(BrewerProfile.is_public==True, cls.is_public==True))
        return query

    @classmethod
    def _last(cls, ordering, public_only=False, limit=5, extra_user=None):
        query = cls.public_query(public_only, extra_user)
        return query.filter(cls.is_draft==False).order_by(desc(ordering)).limit(limit).all()

    @classmethod
    def last_created(cls, public_only=False, limit=5, **kwargs):
        extra_user = kwargs.get('extra_user')
        return cls._last(cls.created, public_only, limit, extra_user)

    @classmethod
    def last_updated(cls, public_only=False, limit=5, **kwargs):
        extra_user = kwargs.get('extra_user')
        return cls._last(cls.updated, public_only, limit, extra_user)

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
    def carbonation_data_display(self):
        if self.carbonation_type:
            data = {
                'carb_type': _(dict(choices.CARBONATION_CHOICES)[self.carbonation_type]),
                'carb_level': _(dict(choices.CARB_LEVEL_CHOICES)[self.carbonation_level or u'normal']),
            }
            return _('%(carb_type)s: carbonation %(carb_level)s', **data)
        return u''

    def has_access(self, user):
        if self.brewery.brewer != user:
            if not (self.is_public and self.brewery.has_access(user)):
                return False
        return True

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
