import datetime

import markdown

from ..ext import db


class Brewery(db.Model):
    __tablename__ = 'brewery'
    id = db.Column(db.Integer, primary_key=True)  # noqa: A003
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    established_date = db.Column(db.Date)
    est_year = db.Column(db.Integer)
    est_month = db.Column(db.Integer)
    est_day = db.Column(db.Integer)
    stats = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow, index=True)
    brewer_id = db.Column(
        db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False
    )
    brewer = db.relationship(
        'BrewerProfile',
        backref=db.backref('breweries', lazy='dynamic', cascade='all,delete-orphan'),
    )


# events: Brewery model
def brewery_pre_save(mapper, connection, target):
    if target.description:
        target.description_html = markdown.markdown(target.description)
    else:
        target.description_html = None
    if target.updated is None:
        target.updated = target.created
    if target.established_date:
        target.est_year = target.established_date.year
        target.est_month = target.established_date.month
        target.est_day = target.established_date.day


db.event.listen(Brewery, 'before_insert', brewery_pre_save)
db.event.listen(Brewery, 'before_update', brewery_pre_save)
