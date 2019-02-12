import datetime

import markdown

from ..ext import db
from ..utils.text import stars2deg
from .brewery import Brewery
from .brewing import Brew, FermentationStep
from .tasting import TastingNote
from .users import BrewerProfile


# events: Brewery model
def brewery_pre_save(mapper, connection, target):
    if target.description:
        target.description_html = markdown.markdown(target.description, safe_mode='remove')
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


# events: Brew model
def brew_pre_save(mapper, connection, target):
    bjcp_style = '%s %s' % (target.bjcp_style_code or '', target.bjcp_style_name or '')
    bjcp_style = bjcp_style.strip()
    target.bjcp_style = bjcp_style or None
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    if target.updated is None:
        target.updated = target.created


db.event.listen(Brew, 'before_insert', brew_pre_save)
db.event.listen(Brew, 'before_update', brew_pre_save)


# events: TastingNote model
def tasting_note_pre_save(mapper, connection, target):
    if target.date is None:
        target.date = datetime.date.today()
    if target.text:
        target.text = stars2deg(target.text)
        target.text_html = markdown.markdown(target.text, safe_mode='remove')


db.event.listen(TastingNote, 'before_insert', tasting_note_pre_save)
db.event.listen(TastingNote, 'before_update', tasting_note_pre_save)


# events: BrewerProfile model
def profile_pre_save(mapper, connection, target):
    full_name = '%s %s' % (target.first_name or '', target.last_name or '')
    target.full_name = full_name.strip()
    if target.updated is None:
        target.updated = target.created


db.event.listen(BrewerProfile, 'before_insert', profile_pre_save)
db.event.listen(BrewerProfile, 'before_update', profile_pre_save)


# events: FermentationStep model
def fermentation_step_pre_save(mapper, connection, target):
    if target.notes:
        target.notes = stars2deg(target.notes)
        target.notes_html = markdown.markdown(target.notes, safe_mode='remove')
    else:
        target.notes_html = None


db.event.listen(FermentationStep, 'before_insert', fermentation_step_pre_save)
db.event.listen(FermentationStep, 'before_update', fermentation_step_pre_save)
