import datetime

from flask import url_for
from flask_babel import lazy_gettext as _
from flask_login import UserMixin

from ..ext import db
from ..utils.models import DefaultModelMixin


class BrewerProfile(UserMixin, db.Model, DefaultModelMixin):
    __tablename__ = 'brewer_profile'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    nick = db.Column(db.String(50))
    email = db.Column(db.String(200), index=True, nullable=False)
    full_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    about_me = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow, index=True)
    access_token = db.Column(db.Text)  # for OAuth2
    oauth_token = db.Column(db.Text)  # for OAuth1a
    oauth_token_secret = db.Column(db.Text)  # for OAuth1a
    oauth_service = db.Column(db.String(50))
    remote_userid = db.Column(db.String(100))

    __table_args__ = (
        db.Index('user_remote_id', 'oauth_service', 'remote_userid'),
    )

    @property
    def absolute_url(self):
        return url_for('profile.details', user_id=self.id)

    @property
    def breweries_list_url(self):
        return url_for('profile.breweries', user_id=self.id)

    @property
    def brews_list_url(self):
        return url_for('profile.brews', user_id=self.id)

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
    def _last(cls, ordering, public_only=False, limit=5):
        query = cls.query
        if public_only:
            query = query.filter_by(is_public=True)
        return query.order_by(db.desc(ordering)).limit(limit).all()

    @classmethod
    def last_created(cls, public_only=False, limit=5, **kwargs):
        return cls._last(cls.created, public_only, limit)

    @classmethod
    def last_updated(cls, public_only=False, limit=5):
        return cls._last(cls.updated, public_only, limit)

    @classmethod
    def public(cls, order_by=None):
        query = cls.query.filter_by(is_public=True)
        if order_by is not None:
            query = query.order_by(order_by)
        return query

    def has_access(self, user):
        if self != user and not self.is_public:
            return False
        return True

    def full_data(self):
        return self.__dict__


# events: BrewerProfile model
def profile_pre_save(mapper, connection, target):
    full_name = '%s %s' % (target.first_name or '', target.last_name or '')
    target.full_name = full_name.strip()
    if target.updated is None:
        target.updated = target.created


db.event.listen(BrewerProfile, 'before_insert', profile_pre_save)
db.event.listen(BrewerProfile, 'before_update', profile_pre_save)


class CustomExportTemplate(db.Model, DefaultModelMixin):
    __tablename__ = 'custom_export_template'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    user = db.relationship(
        'BrewerProfile',
        backref=db.backref(
            'custom_export_templates', cascade='all,delete', lazy='dynamic',
            order_by='CustomExportTemplate.name'
        )
    )
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)

    __table__args__ = (
        db.Index('user_export_template', 'user_id', 'name'),
    )

    @property
    def absolute_url(self):
        return url_for('profile.export_template', tid=self.id, user_id=self.user.id)


class CustomLabelTemplate(db.Model, DefaultModelMixin):
    __tablename__ = 'custom_label_template'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    user = db.relationship(
        'BrewerProfile',
        backref=db.backref(
            'custom_label_templates', cascade='all,delete', lazy='dynamic',
            order_by='CustomLabelTemplate.name'
        )
    )
    name = db.Column(db.String(100), nullable=False)
    cols = db.Column(db.Integer, nullable=False, default=2)
    rows = db.Column(db.Integer, nullable=False, default=5)
    width = db.Column(db.Integer, default=90, server_default='90', nullable=False)
    height = db.Column(db.Integer, default=50, server_default='50', nullable=False)
    text = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.Index('user_label_template', 'user_id', 'name'),
    )

    @property
    def absolute_url(self):
        return url_for('profile.label_template', tid=self.id, user_id=self.user.id)
