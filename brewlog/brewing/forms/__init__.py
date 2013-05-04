from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf import Form

from brewlog import session
from brewlog.brewing import models


TastingNoteForm = model_form(models.TastingNote, db_session=session)

BrewForm = model_form(models.Brew, db_session=session, base_class=Form)
