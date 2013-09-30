from flask import render_template
from flask_login import current_user
from brewlog import pages
from brewlog.models import latest_breweries, latest_brews
from brewlog.models.users import BrewerProfile
from brewlog.models.brewing import Brew, Brewery


def main():
    item_limit = 5
    if current_user.is_authenticated():
        kw = {'extra_user': current_user}
    else:
        kw = {}
    ctx = {
        'latest_brews': latest_brews(Brew.created, limit=item_limit, public_only=True, **kw),
        'latest_breweries': latest_breweries(Brewery.created, limit=item_limit, public_only=True, **kw),
        'latest_brewers': BrewerProfile.last_created(limit=item_limit, public_only=True, **kw),
        'recently_active_breweries': latest_breweries(Brewery.updated, limit=item_limit, public_only=True, **kw),
        'recently_active_brewers': BrewerProfile.last_updated(limit=item_limit, public_only=True, **kw),
    }
    return render_template('home.html', **ctx)

def flatpage(path):
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'flatpage.html')
    return render_template(template, page=page, html=page.html)