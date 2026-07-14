from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt


def role_required(*roles):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            if claims["role"] not in roles:
                return jsonify({
                    "error": "Access denied"
                }), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator