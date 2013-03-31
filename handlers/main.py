# -*- coding: utf-8 -*-

from handlers.base import BaseRequestHandler
from models.simple import Batch
from models.base import Brewery, BrewerProfile

class MainHandler(BaseRequestHandler):

    def get(self):
        item_limit = 5
        ctx = {
            'latest_brews': Batch.query().order(-Batch.created_at).fetch(item_limit),
            'latest_breweries': Brewery.query().order(-Brewery.created).fetch(item_limit),
            'latest_brewers': BrewerProfile.query().order(-BrewerProfile.created).fetch(item_limit),
            'recently_active_breweries': [],
            'recently_active_brewers': [],
            'most_active_breweries': []
        }
        return self.render('home.html', ctx)
