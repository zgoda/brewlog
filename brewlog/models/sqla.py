import datetime

import markdown
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy import event

from database import Model


class Brewery(Model):
    __tablename__ = 'brewery'
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    description_html = Column(Text)
    established_date = Column(Date)
    est_year = Column(Integer)
    est_month = Column(Integer)
    est_day = Column(Integer)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, onupdate=datetime.datetime.now)

    def compute_fields(self):
        self.description_html = markdown.markdown(self.description, safe_mode='remove')
        if self.established_date is not None:
            self.est_year = self.established_date.year
            self.est_month = self.established_date.month
            self.est_day = self.established_date.day

@event.listens_for(Brewery, 'before_insert')
@event.listens_for(Brewery, 'before_update')
def brewery_compute(mapper, connection, target):
    target.compute_fields()


class BrewerProfile(Model):
    __tablename__ = 'brewerprofile'
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

    def compute_fields(self):
        full_name = u'%s %s' % (self.first_name or u'', self.last_name or u'')
        self.full_name = full_name.strip()


@event.listens_for(BrewerProfile, 'before_insert')
@event.listens_for(BrewerProfile, 'before_update')
def brewer_profile_compute(mapper, connection, target):
    target.compute_fields()
