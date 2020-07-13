import markdown
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

    def display_info(self):
        if self.og and self.fg and self.volume:
            line = _(
                'OG: %(og)s&deg;Blg, FG: %(fg)s&deg;Blg, volume: %(volume)s ltr',
                og=self.og, fg=self.fg, volume=self.volume
            )
        elif self.og and self.volume:
            line = _(
                'OG: %(og)s&deg;Blg, volume: %(volume)s ltr',
                og=self.og, volume=self.volume
            )
        elif self.og and self.fg:
            line = _(
                'OG: %(og)s&deg;Blg, FG: %(fg)s&deg;Blg', og=self.og, fg=self.fg
            )
        elif self.og:
            line = _('OG: %(og)s&deg;Blg', og=self.og)
        else:
            line = _('missing key fermentation data')
        return line

    def previous_step(self):
        return FermentationStep.query.filter(
            FermentationStep.brew == self.brew, FermentationStep.date < self.date
        ).order_by(db.desc(FermentationStep.date)).first()

    def next_step(self):
        return FermentationStep.query.filter(
            FermentationStep.brew == self.brew, FermentationStep.date > self.date
        ).order_by(FermentationStep.date).first()

    @classmethod
    def first_for_brew(cls, brew_id):
        return cls.query.filter_by(brew_id=brew_id).order_by(cls.date).first()

    @classmethod
    def last_for_brew(cls, brew_id):
        return cls.query.filter_by(brew_id=brew_id).order_by(db.desc(cls.date)).first()


# events: FermentationStep model
def fermentation_step_pre_save(mapper, connection, target):
    target.notes_html = markdown.markdown(target.notes)


db.event.listen(FermentationStep, 'before_insert', fermentation_step_pre_save)
db.event.listen(FermentationStep, 'before_update', fermentation_step_pre_save)
