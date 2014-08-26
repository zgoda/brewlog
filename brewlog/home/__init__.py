from flask import Blueprint


home_bp = Blueprint('home', __name__)

import brewlog.home.views  # noqa
