from flask import Blueprint


profile_bp = Blueprint('profile', __name__)

import brewlog.profile.views  # noqa
