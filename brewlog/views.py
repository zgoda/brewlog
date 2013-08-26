from flask import render_template
from flask_login import current_user
from brewlog.models import BrewerProfile, Brew, Brewery


def main():
    item_limit = 5
    if current_user.is_authenticated():
        kw = {'extra_user': current_user}
    else:
        kw = {}
    ctx = {
        'latest_brews': Brew.last_created(limit=item_limit, public_only=True, **kw),
        'latest_breweries': Brewery.last_created(limit=item_limit, public_only=True, **kw),
        'latest_brewers': BrewerProfile.last_created(limit=item_limit, public_only=True, **kw),
        'recently_active_breweries': Brewery.last_updated(limit=item_limit, public_only=True, **kw),
        'recently_active_brewers': BrewerProfile.last_updated(limit=item_limit, public_only=True, **kw),
    }
    return render_template('home.html', **ctx)

