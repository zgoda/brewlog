import datetime

from flask import url_for
import peewee as pw
from flask_login import UserMixin

from brewlog import Model
from brewlog.utils.models import DataModelMixin


class BrewerProfile(UserMixin, DataModelMixin, Model):
    first_name = pw.CharField(max_length=50, null=True)
    last_name = pw.CharField(max_length=50, null=True)
    nick = pw.CharField(max_length=50, null=True)
    email = pw.CharField(max_length=80, index=True)
    full_name = pw.CharField(max_length=100, null=True)
    location = pw.CharField(max_length=100, null=True)
    about_me = pw.TextField(null=True)
    is_public = pw.BooleanField(default=True)
    created = pw.DateTimeField(default=datetime.datetime.utcnow)
    updated = pw.DateTimeField(index=True)
    access_token = pw.TextField(null=True) # for OAuth2
    oauth_token = pw.TextField(null=True) # for OAuth1a
    oauth_token_secret = pw.TextField(null=True) # for OAuth1a
    oauth_service = pw.CharField(max_length=50, null=True)
    remote_userid = pw.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'brewer_profile'
        indexes = (
            (('oauth_service', 'remote_userid'), False),
        )

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        full_name = u'%s %s' % (self.first_name or u'', self.last_name or u'')
        self.full_name = full_name.strip()
        self.updated = datetime.datetime.utcnow()
        return super(BrewerProfile, self).save(*args, **kwargs)

    def get_id(self):
        """This has to be overwritten because flask-login wants to convert
        it to unicode, no matter what"""
        if self.id is None:
            return self.id
        return super(BrewerProfile, self).get_id()

    @property
    def absolute_url(self):
        return url_for('profile-details', userid=self.id)

    @property
    def name(self):
        return self.full_name or self.email

    @classmethod
    def last_created(cls, limit=5):
        return cls.select().order_by(cls.created.desc()).limit(limit)

    @classmethod
    def last_updated(cls, limit=5):
        return cls.select().order_by(cls.updated.desc()).limit(limit)

