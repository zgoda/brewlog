from flask import Blueprint


profile_bp = Blueprint('profile', __name__)

from . import views  # noqa
