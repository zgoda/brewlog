import datetime

from brewlog import Model

from sqlalchemy import Table, Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship


brewers_breweries = Table('brewers_breweries', Model.metadata,
    Column('brewer_id', Integer, ForeignKey('brewer_profile.id')),
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
    created = Column(DateTime, default=datetime.datetime.utcnow)
    updated = Column(DateTime, onupdate=datetime.datetime.utcnow)
    brewer_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    brewer = relationship('brewlog.users.models.BrewerProfile', backref='breweries')
    other_brewers = relationship('brewlog.users.models.BrewerProfile',
        secondary=brewers_breweries, backref='other_breweries')
