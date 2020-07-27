from decimal import Decimal

CARBONATION_KEYS = ('forced in keg', 'keg with priming', 'bottles with priming')
CARBONATION_VALUES = (
    'wymuszone w kegu', 'refermentacja w kegu', 'refermentacja w butelkach'
)
CARBONATION_CHOICES = list(zip(CARBONATION_KEYS, CARBONATION_VALUES))

CARB_LEVEL_KEYS = ('high', 'normal', 'low', 'very low', 'none')
CARB_LEVEL_VALUES = (
    'wysokie (np. niemiecka pszenica, belgijskie ale)',
    'normalne (np. lager, amerykańskie ale)',
    'niskie (np. brytyjskie lub irlandzkie ale)',
    'bardzo niskie (np kellerbier)',
    'żadne (np. sahti)',
)
CARB_LEVELS = (Decimal(0.4), Decimal(0.35), Decimal(0.3), Decimal(0.15), Decimal(0))
CARB_LEVEL_DATA = dict(zip(CARB_LEVEL_KEYS, CARB_LEVELS))
CARB_LEVEL_CHOICES = list(zip(CARB_LEVEL_KEYS, CARB_LEVEL_VALUES))
