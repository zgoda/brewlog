# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import datetime

import markdown

from ..ext import db
from ..utils.text import stars2deg


class TastingNote(db.Model):
    __tablename__ = 'tasting_note'
    id = db.Column(db.Integer, primary_key=True)  # noqa: A003
    author_id = db.Column(
        db.Integer, db.ForeignKey('brewer_profile.id'), nullable=False
    )
    author = db.relationship(
        'BrewerProfile',
        backref=db.backref(
            'tasting_notes', cascade='all,delete-orphan', lazy='dynamic'
        )
    )
    date = db.Column(db.Date, nullable=False, index=True)
    text = db.Column(db.Text, nullable=False)
    text_html = db.Column(db.Text)
    brew_id = db.Column(db.Integer, db.ForeignKey('brew.id'), nullable=False)
    brew = db.relationship(
        'Brew',
        backref=db.backref(
            'tasting_notes', cascade='all,delete-orphan', lazy='dynamic',
            order_by='desc(TastingNote.date)'
        )
    )

    @classmethod
    def create_for(cls, brew, author, text, date=None):
        note = cls(brew=brew, author=author, text=text)
        note.date = date or datetime.date.today()
        db.session.add(note)
        db.session.flush()
        return note


# events: TastingNote model
def tasting_note_pre_save(mapper, connection, target):
    target.text = stars2deg(target.text)
    target.text_html = markdown.markdown(target.text, safe_mode='remove')


db.event.listen(TastingNote, 'before_insert', tasting_note_pre_save)
db.event.listen(TastingNote, 'before_update', tasting_note_pre_save)
