# -*- coding: utf-8 -*-

from wtforms.ext.appengine.db import model_form

from models import Brewery


BreweryBaseForm = model_form(Brewery)


class BreweryForm(BreweryBaseForm):
    pass