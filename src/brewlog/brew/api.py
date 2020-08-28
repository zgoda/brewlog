from flask import current_app, jsonify, request
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest

from ..models import Brew
from ..schema import brew_action_schema, brew_schema
from . import brew_api_bp
from .permissions import AccessManager
from .utils import BrewUtils, package_brew


@brew_api_bp.route('/transfer', methods=['POST'])
@login_required
def transfer():
    return jsonify({'op': 'transfer'})


@brew_api_bp.route('/package', methods=['POST'])
@login_required
def package():
    data = brew_action_schema.load(request.json)
    brew_id = data.pop('id')
    brew = Brew.query.get_or_404(brew_id)
    AccessManager(brew, True).check()
    package_brew(brew, **data)


@brew_api_bp.route('/brews')
@login_required
def brews():
    states = request.args.getlist('state')
    if not states:
        raise BadRequest('Brew state requred')
    data = {}
    item_limit = current_app.config.get('SHORTLIST_DEFAULT_LIMIT', 5)
    kw = {
        'user': current_user,
        'public_only': False,
        'limit': item_limit,
    }
    for state in states:
        if state == 'dispensing':
            state = 'on_tap'
        if state == 'recipes':
            state = 'latest'
        state_fetch_method = getattr(BrewUtils, state, None)
        if not state_fetch_method:
            raise BadRequest(f'Unknown state {state}')
        data[state] = brew_schema.dump(state_fetch_method(**kw), many=True)
    return jsonify(data)
