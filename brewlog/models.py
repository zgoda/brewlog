import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey, Date, DateTime, String, Text
from sqlalchemy.orm import relationship, backref
import markdown

from brewlog import Model


other_brewers = Table('other_brewers', Model.metadata,
    Column('brewer_profile_id', Integer, ForeignKey('brewer_profile.id')),
    Column('brewery_id', Integer, ForeignKey('brewery.id')),
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
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, onupdate=datetime.datetime.now)
    brewer_id = Column(Integer, ForeignKey('brewer_profile.id'))
    other_brewers = relationship('BrewerProfile', secondary=other_brewers,
        backref=backref('other_breweries'))

    def __repr__(self):
        return u'<Brewery %s>' % self.name

    def _pre_save(self):
        if self.established_date is not None:
            self.est_year = self.established_date.est_year
            self.est_month = self.established_date.est_month
            self.est_day = self.established_date.day
        if self.description:
            self.description_html = markdown.markdown(self.description)
        if self.updated is None:
            self.updated = self.created


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
    breweries = relationship('Brewery', backref='breweries')

    def __repr__(self):
        return u'<BrewerProfile %s>' % self.email

    def _pre_save(self):
        full_name = u'%s %s' % (self.first_name or u'', self.last_name or u'')
        self.full_name = full_name.strip()
        if self.updated is None:
            self.updated = self.created
