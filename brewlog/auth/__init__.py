from flask import Blueprint


auth_bp = Blueprint('auth', __name__)

import brewlog.auth.views  # noqa
