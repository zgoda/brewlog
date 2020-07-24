from flask import Blueprint


tasting_bp = Blueprint('tastingnote', __name__)

from . import views  # noqa: F401,E402
