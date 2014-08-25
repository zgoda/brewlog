from flask import Blueprint


brew_bp = Blueprint('brew', __name__)

import brewlog.brew.views  # noqa
