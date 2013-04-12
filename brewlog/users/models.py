import datetime

from brewlog import Model

from sqlalchemy import Column, Integer, DateTime, String, Text
from sqlalchemy.orm import relationship


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
    updated = Column(DateTime, onupdate=datetime.datetime.now)
    access_token = Column(Text) # for OAuth2
    oauth_token = Column(Text) # for OAuth1a
    oauth_token_secret = Column(Text) # for OAuth1a
    breweries = relationship('brewlog.brewing.models.Brewery', backref='brewery')

    def __repr__(self):
        return u'<BrewerProfile %s>' % self.email

    def _pre_save(self):
        full_name = u'%s %s' % (self.first_name or u'', self.last_name or u'')
        self.full_name = full_name.strip()
        if self.updated is None:
            self.updated = self.created
