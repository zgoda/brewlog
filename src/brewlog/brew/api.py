from flask import jsonify

from . import brew_api_bp


@brew_api_bp.route('/transfer', methods=['POST'])
def transfer():
    return jsonify({'op': 'transfer'})


def package():
    return jsonify({'op': 'package'})
