from flask import current_app, render_template
from flask_login import current_user

from . import home_bp
from ..brew.utils import BrewUtils
from ..brewery.utils import BreweryUtils
from ..ext import pages
from ..models import latest_tasting_notes
from ..models.brewing import Brew, Brewery
from ..models.tasting import TastingNote
from ..models.users import BrewerProfile


@home_bp.route('/', endpoint='index')
def main():
    if current_user.is_authenticated:
        return dashboard()
    item_limit = current_app.config.get('SHORTLIST_DEFAULT_LIMIT', 5)
    ctx = dict(
        latest_brews=BrewUtils.latest(Brew.created, limit=item_limit, public_only=True),
        latest_breweries=BreweryUtils.latest_breweries(Brewery.created, limit=item_limit, public_only=True),
        latest_brewers=BrewerProfile.last_created(limit=item_limit, public_only=True),
        latest_tasting_notes=latest_tasting_notes(TastingNote.date, limit=item_limit, public_only=True),
        recently_active_breweries=BreweryUtils.latest_breweries(Brewery.updated, limit=item_limit, public_only=True),  # noqa
        recently_active_brewers=BrewerProfile.last_updated(limit=item_limit, public_only=True),
    )
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
        'latest_recipes': BrewUtils.latest(Brew.created, **kw),
        'recently_brewed': BrewUtils.latest(Brew.date_brewed, **brewed_kw),
        'recent_reviews': latest_tasting_notes(TastingNote.date, **kw),
        'fermenting': BrewUtils.fermenting(**kw),
        'maturing': BrewUtils.maturing(**kw),
        'on_tap': BrewUtils.on_tap(**kw),
    }
    return render_template('misc/dashboard.html', **ctx)


@home_bp.route('/pages/<path:path>', endpoint='flatpage')
def flatpage(path):  # pragma: no cover
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'flatpage.html')
    return render_template(template, page=page, html=page.html)
