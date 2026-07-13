from flask import Blueprint, request, jsonify
from services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    user, error = register_user(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    token, error = login_user(data)

    if error:
        return jsonify({"error": error}), 401

    return jsonify({
        "access_token": token
    })