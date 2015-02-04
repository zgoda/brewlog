from flask_babelex import lazy_gettext as _


EVENT_TYPE_KEYS = (
    '',
    'brewing',
    'fermentation start',
    'gravity check',
    'racked',
    'dry hop',
    'fermentation finish',
    'maturation start',
    'maturation finish',
    'package',
    'taste',
)
EVENT_TYPE_VALUES = (
    None,
    _('brewing'),
    _('fermentation start'),
    _('gravity check'),
    _('racked'),
    _('dry hop'),
    _('fermentation finish'),
    _('maturation start'),
    _('maturation finish'),
    _('package'),
    _('taste'),
)

EVENT_TYPE_CHOICES = zip(EVENT_TYPE_KEYS, EVENT_TYPE_VALUES)
