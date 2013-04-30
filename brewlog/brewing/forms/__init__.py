from wtforms.ext.sqlalchemy.orm import model_form
from flask_wtf import Form

from brewlog import session
from brewlog.brewing import models

FermentableItemForm = model_form(models.Fermentable, db_session=session)

HopItemForm = model_form(models.Hop, db_session=session)

YeastItemForm = model_form(models.Yeast, db_session=session)

MiscItemForm = model_form(models.Misc, db_session=session)

MashStepForm = model_form(models.MashStep, db_session=session)

HoppingStepForm = model_form(models.HoppingStep, db_session=session)

AdditionalFermentationStepForm = model_form(models.AdditionalFermentationStep, db_session=session)

TastingNoteForm = model_form(models.TastingNote, db_session=session)

BrewForm = model_form(models.Brew, db_session=session, base_class=Form)
