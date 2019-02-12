import datetime

from ..ext import db
from ..utils.models import DefaultModelMixin


class TastingNote(db.Model, DefaultModelMixin):
    __tablename__ = 'tasting_note'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False)
    author = db.relationship('BrewerProfile')
    date = db.Column(db.Date, nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    text_html = db.Column(db.Text)
    brew_id = db.Column(db.Integer, db.ForeignKey('brew.id'), nullable=False)
    brew = db.relationship(
        'Brew',
        backref=db.backref(
            'tasting_notes', cascade='all,delete', lazy='dynamic', order_by='desc(TastingNote.date)'
        )
    )

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
