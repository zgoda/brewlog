import datetime

from brewlog import db


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

    def __repr__(self):
        return u'<Brewery %s>' % self.name


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
