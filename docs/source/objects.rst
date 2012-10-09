Objects and entities
====================

Main entity: Batch
------------------

Batch properties:

 * brew date
 * brew name
 * notes, description
 * fermentables, list of (generic name, make, market name, amount in grams)
 * hops, list of (variety name, year, AA content, amount in grams), computed fields (GPH,)
 * yeast, list of (manufacturer, strain code, strain name, with starter, rehydrated, reused)
 * misc ingredients, list of (name, amount, use)
 * mash schedule, list of (mash step name, temperature, time, step type, amount decocted or water added)
 * boil time in minutes
 * hopping schedule, list of (addition type, time to flameout or steep, variety, amount)
 * fermentation start date
 * OG in Plato
 * FG in Plato
 * brew length
 * fermentation temperature

Related entities: AdditionalFermentationStep, BottlingStep, TastingNote

Entity: AdditionalFermentationStep
----------------------------------

AdditionalFermentationStep properties:
 
 * date
 * initial amount in litres
 * OG in Plato
 * fermentation temperature
 * FG in Plato

Last fermentation step has to have FG specified.

Entity: BottlingStep
--------------------

BottlingStep properties:
 
 * date
 * final amount incl. priming
 * carbonation type, one of (forced in keg, keg with priming, bottles with priming)

Entity: TastingNote
-------------------

TastingNote properties:
 
 * date
 * rating (in whole numbers from 1 to 5)
 * note text

