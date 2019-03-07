import datetime

from flask import url_for
from flask_babel import lazy_gettext as _
from flask_login import UserMixin

from ..ext import db


class BrewerProfile(UserMixin, db.Model):
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
