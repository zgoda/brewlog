import decimal

"""
Formulas used in brewing calculations.
"""

def sg2plato(sg):
    return 259.0 - (259.0 / sg)

def plato2sg(plato):
    return 259.0 / (259.0 - plato)

def abv(og, fg, from_carbonation=0):
    return ((og - fg) / decimal.Decimal(1.938)) + from_carbonation
