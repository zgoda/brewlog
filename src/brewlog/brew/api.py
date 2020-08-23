from flask import jsonify
from flask_login import login_required

from . import brew_api_bp


@brew_api_bp.route('/transfer', methods=['POST'])
@login_required
def transfer():
    return jsonify({'op': 'transfer'})


@brew_api_bp.route('/package', methods=['POST'])
@login_required
def package():
    return jsonify({'op': 'package'})


@brew_api_bp.route('/brews')
@login_required
def brews():
    return jsonify({'op': 'brews'})
