from decimal import Decimal

from flask_babel import lazy_gettext as _


CARBONATION_KEYS = ('forced in keg', 'keg with priming', 'bottles with priming')
CARBONATION_VALUES = (
    _('forced in keg'), _('keg with priming'), _('bottles with priming')
)
CARBONATION_CHOICES = list(zip(CARBONATION_KEYS, CARBONATION_VALUES))

CARB_LEVEL_KEYS = ('high', 'normal', 'low', 'very low', 'none')
CARB_LEVEL_VALUES = (
    _('high (eg. German wheat, Belgian ales)'),
    _('normal (eg. lagers, American ales)'),
    _('low (eg. British and Irish ales)'),
    _('very low (eg. Scottish ales, kellerbiers)'),
    _('none (eg. Finnish sahti)'),
)
CARB_LEVELS = (Decimal(0.4), Decimal(0.35), Decimal(0.3), Decimal(0.15), Decimal(0))
CARB_LEVEL_DATA = dict(zip(CARB_LEVEL_KEYS, CARB_LEVELS))
CARB_LEVEL_CHOICES = list(zip(CARB_LEVEL_KEYS, CARB_LEVEL_VALUES))

YEAST_USE_KEYS = ('primary', 'secondary', 'bottling')
YEAST_USE_VALUES = (_('primary'), _('secondary'), _('bottling'))
YEAST_USE_CHOICES = list(zip(YEAST_USE_KEYS, YEAST_USE_VALUES))

MISC_USE_KEYS = ('mash', 'boil', 'fermentation', 'bottling')
MISC_USE_VALUES = (_('mash'), _('boil'), _('fermentation'), _('bottling'))
MISC_USE_CHOICES = list(zip(MISC_USE_KEYS, MISC_USE_VALUES))

STEP_TYPE_KEYS = ('infusion', 'decoction', 'temperature')
STEP_TYPE_VALUES = (_('infusion'), _('decoction'), _('temperature'))
STEP_TYPE_CHOICES = list(zip(STEP_TYPE_KEYS, STEP_TYPE_VALUES))

HOPSTEP_TYPE_KEYS = ('mash', 'first wort', 'boil', 'post-boil', 'dry hop')
HOPSTEP_TYPE_VALUES = (
    _('mash'), _('first wort'), _('boil'), _('post-boil'), _('dry hop')
)
HOPSTEP_TYPE_CHOICES = list(zip(HOPSTEP_TYPE_KEYS, HOPSTEP_TYPE_VALUES))

ACTION_KEYS = ('tap', 'untap', 'finish', 'available')
ACTION_VALUES = (_('tap'), _('untap'), _('finish'), _('available'))
ACTION_CHOICES = list(zip(ACTION_KEYS, ACTION_VALUES))
