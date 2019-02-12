import datetime

from flask import url_for
from flask_babel import format_date
from flask_babel import lazy_gettext as _
from sqlalchemy_utils import sort_query

from ..ext import db
from ..utils.models import DefaultModelMixin


class Brewery(db.Model, DefaultModelMixin):
    __tablename__ = 'brewery'
    id = db.Column(db.Integer, primary_key=True)
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
    brewer_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    brewer = db.relationship(
        'BrewerProfile',
        backref=db.backref('breweries', lazy='dynamic', cascade='all,delete')
    )

    @property
    def absolute_url(self):
        return url_for('brewery.details', brewery_id=self.id)

    @property
    def brewers(self):
        return [self.brewer]

    def _brews(self, public_only=False, limit=None, order=None):
        query = self.brews.filter_by(is_draft=False)
        if public_only:
            query = query.filter_by(is_public=True)
        if order is not None:
            query = sort_query(query, order)
        if limit is not None:
            query = query.limit(limit)
        return query

    def recent_brews(self, public_only=False, limit=10):
        return self._brews(public_only=public_only, limit=limit, order='-brew-created')

    def all_brews(self, public_only=False):
        return self._brews(public_only=public_only, order='-brew-created')

    @property
    def render_fields(self):
        return (
            (_('name'), self.name),
            (_('description'), self.description),
            (_('established'), format_date(self.established_date, 'medium')),
        )

    def has_access(self, user):
        if self.brewer != user and not self.brewer.has_access(user):
            return False
        return True