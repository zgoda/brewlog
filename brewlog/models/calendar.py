import markdown

from brewlog import db
from brewlog.utils.models import DefaultModelMixin
from brewlog.models.brewing import Brew, Brewery


class RemoteCalendar(db.Model, DefaultModelMixin):
    __tablename__ = 'remote_calendar'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    user = db.relationship('BrewerProfile')
    service = db.Column(db.String(50), nullable=False)
    remote_id = db.Column(db.String(200), nullable=False)

    def __unicode__(self):  # pragma: no cover
        return u'<RemoteCalendar %s in %s for %s>' % (self.name, self.service, self.user.email)


class Event(db.Model, DefaultModelMixin):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    brew_id = db.Column(db.Integer, db.ForeignKey('brew.id'), nullable=False)
    brew = db.relationship('Brew')
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, index=True)
    event_type = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, default=True)
    calendar_id = db.Column(db.Integer, db.ForeignKey('remote_calendar.id'))
    calendar = db.relationship('RemoteCalendar')

    def __unicode__(self):  # pragma: no cover
        return u'<Event %s for %s>' % (self.title, self.brew.name)

    @classmethod
    def get_latest_for(cls, user, public_only=False, limit=None):
        if not user.is_public and public_only:
            return []
        query = cls.query.join(Brew).join(Brewery).filter(Brewery.brewer==user, Brew.is_public==True)
        if public_only:
            query = query.filter(cls.is_public==True)
        query = query.order_by(db.desc(cls.date))
        if limit is not None:
            query = query.limit(limit)
        return query.all()


## events: Event model
def event_pre_save(mapper, connection, target):
    if target.description:
        target.description_html = markdown.markdown(target.description, safe_mode='remove')
    else:
        target.description_html = None

db.event.listen(Event, 'before_insert', event_pre_save)
db.event.listen(Event, 'before_update', event_pre_save)
