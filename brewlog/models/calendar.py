import markdown
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Date, Boolean
from sqlalchemy import desc, event
from sqlalchemy.orm import relationship

from brewlog.db import Model
from brewlog.models.brewing import Brew, Brewery


class RemoteCalendar(Model):
    __tablename__ = 'remote_calendar'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    user = relationship('BrewerProfile')
    service = Column(String(50), nullable=False)
    remote_id = Column(String(200), nullable=False)

    def __unicode__(self):  # pragma: no cover
        return u'<RemoteCalendar %s in %s for %s>' % (self.name, self.service, self.user.email)


class Event(Model):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew')
    title = Column(String(200), nullable=False)
    description = Column(Text)
    description_html = Column(Text)
    date = Column(Date, nullable=False, index=True)
    event_type = Column(String(100))
    is_public = Column(Boolean, default=True)
    calendar_id = Column(Integer, ForeignKey('remote_calendar.id'))
    calendar = relationship('RemoteCalendar')

    def __unicode__(self):  # pragma: no cover
        return u'<Event %s for %s>' % (self.title, self.brew.name)

    @classmethod
    def get_latest_for(cls, user, public_only=False, limit=None):
        if not user.is_public and public_only:
            return []
        query = cls.query.join(Brew).join(Brewery).filter(Brewery.brewer==user, Brew.is_public==True)
        if public_only:
            query = query.filter(cls.is_public==True)
        query = query.order_by(desc(cls.date))
        if limit is not None:
            query = query.limit(limit)
        return query.all()


## events: Event model
def event_pre_save(mapper, connection, target):
    if target.description:
        target.description_html = markdown.markdown(target.description, safe_mode='remove')
    else:
        target.description_html = None

event.listen(Event, 'before_insert', event_pre_save)
event.listen(Event, 'before_update', event_pre_save)
