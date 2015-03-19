from flask import render_template, current_app
from flask_login import current_user

from brewlog.home import home_bp
from brewlog.ext import pages
from brewlog.models import latest_breweries, latest_brews, latest_tasting_notes
from brewlog.models.users import BrewerProfile
from brewlog.models.brewing import Brew, Brewery
from brewlog.models.tasting import TastingNote


@home_bp.route('/', endpoint='index')
def main():
    if current_user.is_authenticated():
        return dashboard()
    item_limit = current_app.config.get('SHORTLIST_DEFAULT_LIMIT', 5)
    if current_user.is_authenticated():
        kw = {'extra_user': current_user}
    else:
        kw = {}
    ctx = {
        'latest_brews': latest_brews(Brew.created, limit=item_limit, public_only=True, **kw),
        'latest_breweries': latest_breweries(Brewery.created, limit=item_limit, public_only=True, **kw),
        'latest_brewers': BrewerProfile.last_created(limit=item_limit, public_only=True, **kw),
        'latest_tasting_notes': latest_tasting_notes(TastingNote.date, limit=item_limit, public_only=True, **kw),
        'recently_active_breweries': latest_breweries(Brewery.updated, limit=item_limit, public_only=True, **kw),
        'recently_active_brewers': BrewerProfile.last_updated(limit=item_limit, public_only=True, **kw),
    }
    return render_template('home.html', **ctx)


def dashboard():
    item_limit = current_app.config.get('SHORTLIST_DEFAULT_LIMIT', 5)
    kw = {
        'user': current_user,
        'public_only': False,
        'limit': item_limit,
    }
    brewed_kw = kw.copy()
    brewed_kw.update({'brewed_only': True})
    ctx = {
        'latest_recipes': latest_brews(Brew.created, **kw),
        'recently_brewed': latest_brews(Brew.date_brewed, **brewed_kw),
        'recent_reviews': latest_tasting_notes(TastingNote.date, **kw),
    }
    return render_template('misc/dashboard.html', **ctx)


@home_bp.route('/pages/<path:path>', endpoint='flatpage')
def flatpage(path):  # pragma: no cover
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'flatpage.html')
    return render_template(template, page=page, html=page.html)
