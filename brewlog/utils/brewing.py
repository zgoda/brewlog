"""
Formulas used in brewing calculations.
"""


def sg2plato(sg):
    """Convert Specific Gravity to Plato
    """
    return 259.0 - (259.0 / float(sg))


def plato2sg(plato):
    """Convert Plat to Specific Gravity
    """
    return 259.0 / (259.0 - float(plato))


def abv(og, fg, from_carbonation=0):
    """Work out alcohol content from fermentation data (optionally including carbonation)
    """
    value = (float(og - fg) / 1.938) + float(from_carbonation)
    return float(value)


def aa(og, fg):
    """Apparent attenuation
    """
    return 100.0 * (og - fg) / og


def ra(og, fg):
    """Real attenuation
    """
    return 0.8192 * aa(og, fg)
