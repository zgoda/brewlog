from flask import Blueprint

ferm_bp = Blueprint('ferm', __name__)

from . import views  # noqa
