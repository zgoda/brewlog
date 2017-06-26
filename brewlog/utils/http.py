import json

from flask import current_app


def json_response(data, code=200, headers=None):
    return current_app.response_class(
        response=json.dumps(data),
        headers=headers,
        status=code,
        mimetype='application/json',
    )
