from flask import Blueprint


brewery_bp = Blueprint('brewery', __name__)

import brewlog.brewery.views  # noqa
