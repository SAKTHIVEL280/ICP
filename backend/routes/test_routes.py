from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from middleware.role_required import role_required

test_bp = Blueprint("test", __name__)

@test_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    claims = get_jwt()

    return jsonify({
        "user_id": get_jwt_identity(),
        "name": claims["name"],
        "role": claims["role"]
    })


@test_bp.route("/admin")
@jwt_required()
@role_required("Administrator")
def admin():

    return {
        "message": "Welcome Admin"
    }