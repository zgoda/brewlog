from wtforms.ext.sqlalchemy.orm import model_form

from brewlog import session
from brewlog.brewing import models


TastingNoteForm = model_form(models.TastingNote, db_session=session)
