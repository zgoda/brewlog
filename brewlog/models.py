import datetime

import markdown

from brewlog import db


other_brewers = db.Table('other_brewers',
    db.Column('brewer_profile_id', db.Integer, db.ForeignKey('brewer_profile.id')),
    db.Column('brewery_id', db.Integer, db.ForeignKey('brewery.id')),
    db.Column('date_joined', db.Date),
)


class Brewery(db.Model):
    __tablename__ = 'brewery'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    established_date = db.Column(db.Date)
    est_year = db.Column(db.Integer)
    est_month = db.Column(db.Integer)
    est_day = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    brewer_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'))
    other_brewers = db.relationship('BrewerProfile', secondary=other_brewers,
        backref=db.backref('other_breweries'))

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


class BrewerProfile(db.Model):
    __tablename__ = 'brewer_profile'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    nick = db.Column(db.String(50))
    email = db.Column(db.String(80), nullable=False)
    full_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    about_me = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.now)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    breweries = db.relationship('Brewery', backref='breweries')

    def __repr__(self):
        return u'<BrewerProfile %s>' % self.email

    def _pre_save(self):
        full_name = u'%s %s' % (self.first_name or u'', self.last_name or u'')
        self.full_name = full_name.strip()
        if self.updated is None:
            self.updated = self.created
