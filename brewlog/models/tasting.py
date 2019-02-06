import datetime

import markdown

from ..ext import db
from ..utils.models import DefaultModelMixin
from ..utils.text import stars2deg


class TastingNote(db.Model, DefaultModelMixin):
    __tablename__ = 'tasting_note'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    author = db.relationship('BrewerProfile')
    date = db.Column(db.Date, nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    text_html = db.Column(db.Text)
    brew_id = db.Column(db.Integer, db.ForeignKey('brew.id'), nullable=False)
    brew = db.relationship('Brew')

    @classmethod
    def create_for(cls, brew, author, text, date=None, commit=False):
        note = cls(brew=brew, author=author, text=text)
        if date is None:
            date = datetime.date.today()
        note.date = date
        db.session.add(note)
        db.session.flush()
        if commit:
            db.session.commit()
        return note


# events: TastingNote model
def tasting_note_pre_save(mapper, connection, target):
    if target.date is None:
        target.date = datetime.date.today()
    if target.text:
        target.text = stars2deg(target.text)
        target.text_html = markdown.markdown(target.text, safe_mode='remove')


db.event.listen(TastingNote, 'before_insert', tasting_note_pre_save)
db.event.listen(TastingNote, 'before_update', tasting_note_pre_save)
