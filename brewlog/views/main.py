# -*- coding: utf-8 -*-

from flask import render_template

from brewlog import app
from brewlog.brewing.models import Brew, Brewery
from brewlog.users.models import BrewerProfile


@app.route('/')
def main():
    item_limit = 5
    ctx = {
        'latest_brews': Brew.query.all().order(-Batch.created_at).fetch(item_limit),
        'latest_breweries': Brewery.query().order(-Brewery.created).fetch(item_limit),
        'latest_brewers': BrewerProfile.query().order(-BrewerProfile.created).fetch(item_limit),
        'recently_active_breweries': [],
        'recently_active_brewers': [],
        'most_active_breweries': []
    }
    return render_template('home.html', **ctx)

