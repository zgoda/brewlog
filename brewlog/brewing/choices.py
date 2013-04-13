# -*- coding: utf-8 -*-

from flaskext.babel import lazy_gettext as _


CARBONATION_KEYS = (u'forced in keg', u'keg with priming', u'bottles with priming')
CARBONATION_VALUES = (_('forced in keg'), _('keg with priming'), _('bottles with priming'))
CARBONATION_CHOICES = zip(CARBONATION_KEYS, CARBONATION_VALUES)

YEAST_USE_KEYS = (u'primary', u'secondary', u'bottling')
YEAST_USE_VALUES = (_('primary'), _('secondary'), _('bottling'))
YEAST_USE_CHOICES = zip(YEAST_USE_KEYS, YEAST_USE_VALUES)

MISC_USE_KEYS = (u'mash', u'boil', u'fermentation', u'bottling')
MISC_USE_VALUES = (_('mash'), _('boil'), _('fermentation'), _('bottling'))
MISC_USE_CHOICES = zip(MISC_USE_KEYS, MISC_USE_VALUES)

STEP_TYPE_KEYS = (u'infusion', u'decoction', u'temperature')
STEP_TYPE_VALUES = (_('infusion'), _('decoction'), _('temperature'))
STEP_TYPE_CHOICES = zip(STEP_TYPE_KEYS, STEP_TYPE_VALUES)

HOPSTEP_TYPE_KEYS = (u'mash', u'first wort', u'boil', u'post-boil', u'dry hop')
HOPSTEP_TYPE_VALUES = (_('mash'), _('first wort'), _('boil'), _('post-boil'), _('dry hop'))
HOPSTEP_TYPE_CHOICES = zip(HOPSTEP_TYPE_KEYS, HOPSTEP_TYPE_VALUES)
