import decimal

"""
Formulas used in brewing calculations.
"""

def sg2plato(sg):
    """Convert Specific Gravity to Plato
    """
    return 259.0 - (259.0 / sg)

def plato2sg(plato):
    """Convert Plat to Specific Gravity
    """
    return 259.0 / (259.0 - plato)

def abv(og, fg, from_carbonation=0):
    """Work out alcohol content from fermentation data (optionally including carbonation)
    """
    value = (decimal.Decimal(og - fg) / decimal.Decimal(1.938)) + decimal.Decimal(from_carbonation)
    return float(value)

def aa(og, fg):
    """Apparent attenuation
    """
    return 100.0 * (og - fg) / og

def ra(og, fg):
    """Real attenuation
    """
    return 0.8192 * aa(og, fg)
