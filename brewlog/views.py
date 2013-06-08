from flask import render_template
from brewlog.models import BrewerProfile, Brew, Brewery


def main():
    item_limit = 5
    ctx = {
        'latest_brews': Brew.last_created(limit=item_limit, public_only=True),
        'latest_breweries': Brewery.last_created(limit=item_limit, public_only=True),
        'latest_brewers': BrewerProfile.last_created(limit=item_limit, pubic_only=True),
        'recently_active_breweries': Brewery.last_updated(limit=item_limit, public_only=True),
        'recently_active_brewers': BrewerProfile.last_updated(limit=item_limit, public_only=True),
    }
    return render_template('home.html', **ctx)

