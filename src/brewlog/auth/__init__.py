from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import views  # noqa: F401,E402
