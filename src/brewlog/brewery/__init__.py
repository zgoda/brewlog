from flask import Blueprint


brewery_bp = Blueprint('brewery', __name__)

from . import views  # noqa
