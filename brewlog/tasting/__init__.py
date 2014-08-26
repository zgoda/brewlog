from flask import Blueprint


tasting_bp = Blueprint('tastingnote', __name__)

import brewlog.tasting.views  # noqa
