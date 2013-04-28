from flask import render_template

from brewlog.brewing.models import Brew, Brewery
from brewlog.users.models import BrewerProfile


def main():
    item_limit = 5
    ctx = {
        'latest_brews': Brew.query.order_by('-created').limit(item_limit).all(),
        'latest_breweries': Brewery.query.order_by('-created').limit(item_limit).all(),
        'latest_brewers': BrewerProfile.query.order_by('-created').limit(item_limit).all(),
        'recently_active_breweries': [],
        'recently_active_brewers': [],
        'most_active_breweries': []
    }
    return render_template('home.html', **ctx)

