# Copyright 2012, 2019 Jarek Zgoda. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from flask_babel import lazy_gettext as _

from ..ext import db


class FermentationStep(db.Model):
    __tablename__ = 'fermentation_step'
    id = db.Column(db.Integer, primary_key=True)  # noqa: A003
    date = db.Column(db.Date, index=True, nullable=False)
    name = db.Column(db.String(200))
    og = db.Column(db.Float(precision=1))
    fg = db.Column(db.Float(precision=1))
    volume = db.Column(db.Float(precision=2))
    temperature = db.Column(db.Integer)
    notes = db.Column(db.Text)
    notes_html = db.Column(db.Text)
    brew_id = db.Column(db.Integer, db.ForeignKey('brew.id'), nullable=False)
    brew = db.relationship(
        'Brew',
        backref=db.backref(
            'fermentation_steps', cascade='all,delete-orphan', lazy='dynamic'
        )
    )

    __table_args__ = (
        db.Index('fermentationstep_brew_date', 'brew_id', 'date'),
    )

    def step_data(self):
        return {
            'og': self.og or _('unspecified'),
            'fg': self.fg or _('unspecified'),
            'volume': self.volume or _('unspecified'),
        }

    def previous_step(self):
        return FermentationStep.query.filter(
            FermentationStep.brew == self.brew, FermentationStep.date < self.date
        ).order_by(db.desc(FermentationStep.date)).first()

    def next_step(self):
        return FermentationStep.query.filter(
            FermentationStep.brew == self.brew, FermentationStep.date > self.date
        ).order_by(FermentationStep.date).first()
