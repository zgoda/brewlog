import datetime

from brewlog import Model

from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy import event


class BrewerProfile(Model):
    __tablename__ = 'brewer_profile'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    nick = Column(String(50))
    email = Column(String(80), nullable=False)
    full_name = Column(String(100))
    location = Column(String(100))
    about_me = Column(Text)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, onupdate=datetime.datetime.now, index=True)
    access_token = Column(Text) # for OAuth2
    oauth_token = Column(Text) # for OAuth1a
    oauth_token_secret = Column(Text) # for OAuth1a
    oauth_service = Column(String(50))

    def __repr__(self):
        return '<BrewerProfile %s>' % self.email.encode('utf-8')

    @property
    def absolute_url(self):
        return ''


# mapper events
def profile_pre_save(mapper, connection, target):
    full_name = u'%s %s' % (target.first_name or u'', target.last_name or u'')
    target.full_name = full_name.strip()
    if target.updated is None:
        target.updated = target.created

event.listen(BrewerProfile, 'before_insert', profile_pre_save)
event.listen(BrewerProfile, 'before_update', profile_pre_save)
