from flask import render_template

from brewlog.brewing.models import Brew, Brewery
from brewlog.users.models import BrewerProfile


def main():
    item_limit = 5
    ctx = {
        'latest_brews': Brew.last_created(limit=item_limit),
        'latest_breweries': Brewery.last_created(limit=item_limit),
        'latest_brewers': BrewerProfile.last_created(limit=item_limit),
        'recently_active_breweries': Brewery.last_updated(limit=item_limit),
        'recently_active_brewers': BrewerProfile.last_updated(limit=item_limit),
    }
    return render_template('home.html', **ctx)

