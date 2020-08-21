from flask import Blueprint

brew_bp = Blueprint('brew', __name__)
brew_api_bp = Blueprint('brew-api', __name__)

from . import api, views  # noqa: F401, E402
