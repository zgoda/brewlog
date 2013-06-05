from decimal import Decimal

from flaskext.babel import lazy_gettext as _


CARBONATION_KEYS = (u'forced in keg', u'keg with priming', u'bottles with priming')
CARBONATION_VALUES = (_('forced in keg'), _('keg with priming'), _('bottles with priming'))
CARBONATION_CHOICES = zip(CARBONATION_KEYS, CARBONATION_VALUES)

CARB_LEVEL_KEYS = (u'high', u'normal', u'low', u'very low', u'none')
CARB_LEVEL_VALUES = (
    _('high (eg. German wheat, Belgian ales)'),
    _('normal (eg. lagers, American ales)'),
    _('low (eg. British and Irish ales)'),
    _('very low (eg. Scottish ales, kellerbiers)'),
    _('none (eg. Finnish sahti)'),
)
CARB_LEVELS = (Decimal(0.4), Decimal(0.35), Decimal(0.3), Decimal(0.15), Decimal(0))
CARB_LEVEL_DATA = dict(zip(CARB_LEVEL_KEYS, CARB_LEVELS))
CARB_LEVEL_CHOICES = zip(CARB_LEVEL_KEYS, CARB_LEVEL_VALUES)

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


BJCP_STYLE_CODES = ('1A', '1B', '1C', '1D', '1E', '2A', '2B', '2C', '3A', '3B', '4A', '4B', '4C',
    '5A', '5B', '5C', '5D', '6A', '6B', '6C', '6D', '7A', '7B', '7C', '8A', '8B', '8C',
    '9A', '9B', '9C', '9D', '9E', '10A', '10B', '10C', '11A', '11B', '11C', '12A', '12B', '12C',
    '13A', '13B', '13C', '13D', '13E', '13F', '14A', '14B', '14C', '15A', '15B', '15C', '15D',
    '16A', '16B', '16C', '16D', '16E', '17A', '17B', '17C', '17D', '17E', '17F',
    '18A', '18B', '18C', '18D', '18E', '19A', '19B', '19C', '20A', '21A', '21B',
    '22A', '22B', '22C', '23A', '24A', '24B', '24C', '25A', '25B', '25C', '26A', '26B', '26C',
    '27A', '27B', '27C', '27D', '27E', '28A', '28B', '28C', '28D')
BJCP_STYLE_NAMES = ('Lite American Lager', 'Standard American Lager', 'Premium American Lager',
    'Munich Helles', 'Dortmunder Export', 'German Pilsner (Pils)', 'Bohemian Pilsener', 'Classic American Pilsner',
    'Vienna Lager', u'Oktoberfest/M\xe4rzen', 'Dark American Lager', 'Munich Dunkel',
    'Schwarzbier (Black Beer)', 'Maibock/Helles Bock', 'Traditional Bock', 'Doppelbock', 'Eisbock',
    'Cream Ale', 'Blonde Ale', u'K\xf6lsch', 'American Wheat or Rye Beer', 'Northern German Altbier',
    'California Common Beer', u'D\xfcsseldorf Altbier', 'Standard/Ordinary Bitter', 'Special/Best/Premium Bitter',
    'Extra Special/Strong Bitter (English Pale Ale)', 'Scottish Light 60/-', 'Scottish Heavy 70/-',
    'Scottish Export 80/-', 'Irish Red Ale', 'Strong Scotch Ale', 'American Pale Ale', 'American Amber Ale',
    'American Brown Ale', 'Mild', 'Southern English Brown', 'Northern English Brown Ale', 'Brown Porter',
    'Robust Porter', 'Baltic Porter', 'Dry Stout', 'Sweet Stout', 'Oatmeal Stout', 'Foreign Extra Stout',
    'American Stout', 'Russian Imperial Stout', 'English IPA', 'American IPA', 'Imperial IPA', 'Weizen/Weissbier',
    'Dunkelweizen', 'Weizenbock', 'Roggenbier (German Rye Beer)', 'Witbier', 'Belgian Pale Ale', 'Saison',
    u'Bi\xe8re de Garde', 'Belgian Specialty Ale', 'Berliner Weisse', 'Flanders Red Ale',
    'Flanders Brown Ale/Oud Bruin', 'Straight (Unblended) Lambic', 'Gueuze', 'Fruit Lambic',
    'Belgian Blond Ale', 'Belgian Dubbel', 'Belgian Tripel', 'Belgian Golden Strong Ale',
    'Belgian Dark Strong Ale', 'Old Ale', 'English Barleywine', 'American Barleywine', 'FRUIT BEER',
    'Spice, Herb, or Vegetable Beer', 'Christmas/Winter Specialty Spiced Beer', 'Classic Rauchbier',
    'Other Smoked Beer', 'Wood-Aged Beer', 'Specialty Beer', 'Dry Mead', 'Semi-sweet Mead', 'Sweet Mead', 'Cyser',
    'Pyment', 'Other Fruit Melomel', 'Metheglin', 'Braggot', 'Open Category Mead', 'Common Cider ', 'English Cider ',
    'French Cider', 'Common Perry', 'Traditional Perry ', 'New England Cider', 'Fruit Cider', 'Applewine',
    'Other Specialty Cider/Perry')
BJCP_STYLES = zip(BJCP_STYLE_CODES, BJCP_STYLE_NAMES)
