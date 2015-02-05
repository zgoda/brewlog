"""
Formulas used in brewing calculations.
"""


def sg2plato(sg):  # pragma: no cover
    """Convert Specific Gravity to Plato
    """
    return 259.0 - (259.0 / sg)


def plato2sg(plato):  # pragma: no cover
    """Convert Plat to Specific Gravity
    """
    return 259.0 / (259.0 - plato)


def abv(og, fg, from_carbonation=0):  # pragma: no cover
    """Work out alcohol content from fermentation data (optionally including carbonation)
    """
    value = (float(og - fg) / 1.938) + float(from_carbonation)
    return float(value)


def aa(og, fg):  # pragma: no cover
    """Apparent attenuation
    """
    return 100.0 * (og - fg) / og


def ra(og, fg):  # pragma: no cover
    """Real attenuation
    """
    return 0.8192 * aa(og, fg)
