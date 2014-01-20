import datetime

import markdown
from sqlalchemy import event, desc
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, ForeignKey, Date

from brewlog.db import Model, session
from brewlog.utils.text import stars2deg


class TastingNote(Model):
    __tablename__ = 'tasting_note'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('brewer_profile.id'), nullable=False)
    author = relationship('BrewerProfile')
    date = Column(Date, nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_html = Column(Text)
    brew_id = Column(Integer, ForeignKey('brew.id'), nullable=False)
    brew = relationship('Brew')

    def __unicode__(self):
        return u'<TastingNote by %s for %s>' % (self.author.name, self.brew.name)

    @classmethod
    def latest(cls, limit=10):
        return cls.query.order_by(desc(cls.date)).limit(limit).all()

    @classmethod
    def create_for(cls, brew, author, text, date=None, commit=False):
        note = cls(brew=brew, author=author, text=text)
        if date is None:
            date = datetime.date.today()
        note.date = date
        session.add(note)
        session.flush()
        if commit:
            session.commit()
        return note

## events: TastingNote model
def tasting_note_pre_save(mapper, connection, target):
    if target.date is None:
        target.date = datetime.date.today()
    if target.text:
        target.text = stars2deg(target.text)
        target.text_html = markdown.markdown(target.text, safe_mode='remove')
    else:
        target.text_html = None

event.listen(TastingNote, 'before_insert', tasting_note_pre_save)
event.listen(TastingNote, 'before_update', tasting_note_pre_save)
