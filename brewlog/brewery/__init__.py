from flask import Blueprint


brew_bp = Blueprint('brewery', __name__)

import brewlog.brewery.views  # noqa
