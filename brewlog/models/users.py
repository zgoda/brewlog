import datetime

from flask import url_for
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index, ForeignKey
from sqlalchemy import event, desc, or_
from sqlalchemy.orm import relationship
from flask_babel import lazy_gettext as _
from flask_login import UserMixin

from brewlog.db import Model
from brewlog.utils.text import slugify
from brewlog.utils.models import DataModelMixin


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
    breweries = relationship('Brewery', cascade='all,delete', lazy='dynamic')
    ipboard_setups = relationship('IPBoardExportSetup', cascade='all,delete')
    custom_export_templates = relationship('CustomExportTemplate', cascade='all,delete')
    custom_label_templates = relationship('CustomLabelTemplate', cascade='all,delete')
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
    is_default = Column(Boolean, default=False)
    __table__args__ = (
        Index('user_export_template', 'user_id', 'name'),
    )

    def __repr__(self):
        return '<ExportTemplate %s for %s>' % (self.name.encode('utf-8'), self.user.email.encode('utf-8'))

    @property
    def absolute_url(self):
        return url_for('profile-export_template', tid=self.id, userid=self.user.id)


class CustomLabelTemplate(Model):
    __tablename__ = 'custom_label_template'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    user = relationship('BrewerProfile')
    name = Column(String(100), nullable=False)
    cols = Column(Integer, nullable=False, default=2)
    rows = Column(Integer, nullable=False, default=5)
    width = Column(Integer, default=90, server_default='90', nullable=False)
    height = Column(Integer, default=50, server_default='50', nullable=False)
    text = Column(Text)
    is_default = Column(Boolean, default=False)
    __table_args__ = (
        Index('user_label_template', 'user_id', 'name'),
    )

    def __repr__(self):
        return '<LabelTemplate %s for %s>' % (self.name.encode('utf-8'), self.user.email.encode('utf-8'))

    @property
    def absolute_url(self):
        return url_for('profile-label_template', tid=self.id, userid=self.user.id)
