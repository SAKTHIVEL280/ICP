from flask import Blueprint, request, jsonify # for importing the Blueprint(used to organize your application into smaller, modular components. ), request, and jsonify(convert Python data structures (like dictionaries or lists) into a proper JSON response) functions from flask

from services.auth_service import register_user 

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    user = register_user(data)

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201