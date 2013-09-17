import operator

from xml.etree import cElementTree as etree
from dateutil import parser

from brewlog.db import session
from brewlog.utils.brewing import sg2plato


def import_beerxml(filename, brewery, save=True):
    imported = []
    tree = etree.parse(filename)
    root = tree.getroot()
    if root.tag != 'RECIPES':
        raise ValueError('file %s does not contain recipes' % filename)
    recipes = root.findall('RECIPE')
    if len(recipes) == 0:
        raise ValueError('no recipes found in file %s' % filename)
    for recipe in recipes:
        brew = brewery.create_brew()
        brew.name = recipe.find('NAME').text
        brew.date_brewed = parser.parse(recipe.find('DATE').text)
        style = recipe.find('STYLE')
        brew.bjcp_style_name = style.find('NAME').text
        brew.bjcp_style_code = '%s%s' % (style.find('CATEGORY_NUMBER').text, style.find('STYLE_LETTER').text)
        brew.brew_length = float(recipe.find('BATCH_SIZE').text)
        brew.boil_time = int(recipe.find('BOIL_TIME').text)
        brew.og = sg2plato(float(recipe.find('OG').text))
        brew.fg = sg2plato(float(recipe.find('FG').text))
        brew.fermentation_temperature = int(float(recipe.find('PRIMARY_TEMP').text))
        # fermentables
        fermentables = []
        for fermentable in recipe.find('FERMENTABLES').findall('FERMENTABLE'):
            name = fermentable.find('NAME').text
            supplier = fermentable.find('SUPPLIER').text
            amount = float(fermentable.find('AMOUNT').text)
            if supplier:
                fermentables.append(u'%(name)s (%(supplier)s) %(amount).2fkg' % locals())
            else:
                fermentables.append(u'%(name)s %(amount).2fkg' % locals())
        if fermentables:
            brew.fermentables = u'\n'.join(fermentables)
        # hops: list and schedule
        hop_schedule = {}
        hop_schedule_list = []
        hops = {}
        hops_list = []
        for hop in recipe.find('HOPS').findall('HOP'):
            name = hop.find('NAME').text
            aa = float(hop.find('ALPHA').text)
            amount = int(float(hop.find('AMOUNT').text) * 1000.0)
            use = hop.find('USE').text.lower()
            time = int(float(hop.find('TIME').text))
            hops[(name, aa)] = hops.get((name, aa), 0) + amount
            hop_schedule[(use, time, name)] = u'%s %s g' % (name, amount)
        for item in sorted(hops.iteritems(), key=operator.itemgetter(1), reverse=True):
            key, amount = item
            name, aa = key
            hops_list.append(u'%s %s%% a-a %s g' % (name, aa, amount))
        if hops_list:
            brew.hops = u'\n'.join(hops_list)
        mash, boil, dry = [], [], []
        for item in hop_schedule.iteritems():
            key, line = item
            use, time, name = key
            if use == 'mash':
                mash.append((time, u'%s (mash)' % line))
            elif use == 'first wort':
                boil.append((time, u'%s (first wort)' % line))
            elif use == 'boil':
                boil.append((time, u'%s (boil)' % line))
            elif use == 'aroma':
                boil.append((0, u'%s (aroma)' % line))
            elif use == 'dry hop':
                dry.append((int(time / 60.0 / 24.0), u'%s (dry hop)' % line))
        for schedule in (mash, boil, dry):
            for item in sorted(schedule, key=operator.itemgetter(0), reverse=True):
                time, line = item
                if schedule == dry:
                    hop_schedule_list.append(u'%s days %s' % (time, line))
                else:
                    hop_schedule_list.append(u'%s\' %s' % (time, line))
        if hop_schedule_list:
            brew.hopping_steps = u'\n'.join(hop_schedule_list)
        # mash
        steps = recipe.find('MASH').find('MASH_STEPS')
        if steps is not None:
            mash_steps = []
            for mash_step in steps.findall('MASH_STEP'):
                name = mash_step.find('NAME').text
                step_type = mash_step.find('TYPE').text.lower()
                if step_type == 'decoction':
                    amount = float(mash_step.find('DECOCTION_AMT').text)
                elif step_type == 'infusion':
                    amount = float(mash_step.find('INFUSE_AMOUNT').text)
                else:
                    amount = 0
                time = int(float(mash_step.find('STEP_TIME').text))
                step_temp = float(mash_step.find('STEP_TEMP').text)
                mash_steps.append(u'%s\' - %s\xb0 %s (%s of %s l)' % (time, step_temp, name, step_type, amount))
            if mash_steps:
                brew.mash_steps = u'\n'.join(mash_steps)
        # misc items
        items = []
        for item in recipe.find('MISCS').findall('MISC'):
            name = item.find('NAME').text
            item_type = item.find('TYPE').text.lower()
            amount = float(item.find('AMOUNT').text) * 1000
            is_weight = item.find('AMOUNT_IS_WEIGHT').text.strip()
            if is_weight:
                is_weight = is_weight == 'true'
            if is_weight:
                units = u'g'
            else:
                units = u'ml'
            items.append(u'%s (%s) %.0f %s' % (name, item_type, amount, units))
        if items:
            brew.misc = u'\n'.join(items)
        # yeast
        items = []
        for item in recipe.find('YEASTS').findall('YEAST'):
            prod_id = item.find('PRODUCT_ID').text or u''
            name = item.find('NAME').text
            lab = item.find('LABORATORY').text or u''
            line = u'%s %s' % (prod_id, name)
            items.append(line.strip())
        if items:
            brew.yeast = u'\n'.join(items)
        if save:
            session.add(brew)
        imported.append(brew)
    if save:
        session.commit()
    return imported, 0