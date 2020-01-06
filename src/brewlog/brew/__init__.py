from flask import Blueprint


brew_bp = Blueprint('brew', __name__)

from . import views  # noqa
