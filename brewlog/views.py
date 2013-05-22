from flask import render_template
from sqlalchemy import desc

from brewlog.brewing.models import Brew, Brewery
from brewlog.users.models import BrewerProfile


def main():
    item_limit = 5
    ctx = {
        'latest_brews': Brew.query.order_by(desc(Brew.created)).limit(item_limit).all(),
        'latest_breweries': Brewery.query.order_by(desc(Brewery.created)).limit(item_limit).all(),
        'latest_brewers': BrewerProfile.query.order_by(desc(BrewerProfile.created)).limit(item_limit).all(),
        'recently_active_breweries': Brewery.query.order_by(desc(Brewery.updated)).limit(item_limit).all(),
        'recently_active_brewers': BrewerProfile.query.order_by(desc(BrewerProfile.updated)).limit(item_limit).all(),
    }
    return render_template('home.html', **ctx)

