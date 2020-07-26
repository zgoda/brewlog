from flask import current_app, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..brew.utils import BrewUtils
from ..brewery.utils import BreweryUtils
from ..ext import pages
from ..models import Brew, BrewerProfile, Brewery, TastingNote
from ..schema import brew_schema
from ..tasting.utils import TastingUtils
from ..utils.text import get_announcement
from . import home_bp


@home_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('.dashboard'))
    item_limit = current_app.config.get('SHORTLIST_DEFAULT_LIMIT', 5)
    ctx = {
        'latest_brews': BrewUtils.latest(
            Brew.created, limit=item_limit, public_only=True
        ),
        'latest_breweries': BreweryUtils.latest_breweries(
            Brewery.created, limit=item_limit, public_only=True
        ),
        'latest_brewers': BrewerProfile.last_created(
            limit=item_limit, public_only=True
        ),
        'latest_tasting_notes': TastingUtils.latest_notes(
            TastingNote.date, limit=item_limit, public_only=True
        ),
        'announcement': get_announcement(current_app.config.get('ANNOUNCEMENT_FILE')),
    }
    ctx['has_content'] = (
        ctx['latest_brews'] and ctx['latest_breweries']
        and ctx['latest_brewers'] and ctx['latest_tasting_notes']
    )
    return render_template('home.html', **ctx)


@home_bp.route('/dashboard')
@login_required
def dashboard():
    item_limit = current_app.config.get('SHORTLIST_DEFAULT_LIMIT', 5)
    kw = {
        'user': current_user,
        'public_only': False,
        'limit': item_limit,
    }
    ctx = {
        'latest_recipes': brew_schema.dump(
            BrewUtils.latest(Brew.created, **kw), many=True
        ),
        'recently_brewed': BrewUtils.latest(Brew.date_brewed, brewed_only=True, **kw),
        'recent_reviews': TastingUtils.latest_notes(TastingNote.date, **kw),
        'fermenting': brew_schema.dump(BrewUtils.fermenting(**kw), many=True),
        'maturing': brew_schema.dump(BrewUtils.maturing(**kw), many=True),
        'on_tap': brew_schema.dump(BrewUtils.on_tap(**kw), many=True),
        'announcement': get_announcement(current_app.config.get('ANNOUNCEMENT_FILE')),
    }
    return render_template('misc/dashboard.html', **ctx)


@home_bp.route('/pages/<path:path>')
def flatpage(path):
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'flatpage.html')
    return render_template(template, page=page)
