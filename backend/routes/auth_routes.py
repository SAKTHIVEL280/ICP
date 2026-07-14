from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import register_user, login_user
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@jwt_required()
def register():
    """
    POST /api/auth/register
    Creates a new user account.
    Restricted to Administrators and Managers.
    - Administrators can create any user role.
    - Managers can only create users in their own department (enforced automatically)
      and are restricted to registering 'Employee' or 'Technician' roles.
    """
    # Read security claims from JWT token
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())
    
    # Restrict endpoint access
    if role != "Administrator" and role != "Manager":
        return jsonify({"error": "Access denied. Manager or Administrator role required."}), 403
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing registration payload."}), 400
        
    # Check for required fields to prevent KeyErrors
    required_fields = ["employee_id", "name", "email", "password", "role"]
    missing_fields = [f for f in required_fields if f not in data or not data[f]]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
    # Enforce manager rules
    if role == "Manager":
        manager = User.query.filter_by(id=user_id).first()
        if not manager or not manager.department_id:
            return jsonify({"error": "Manager department context not found."}), 400
            
        # Overwrite department ID to the manager's own department
        data["department_id"] = manager.department_id
        
        # Managers cannot create other managers or admins
        if data.get("role") not in ["Employee", "Technician"]:
            return jsonify({"error": "Managers can only register Employee or Technician accounts."}), 400
            
    # Call core registration service (hashes password and inserts into DB)
    user, error = register_user(data)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Authenticates a user and returns a signed JWT access token.
    """
    data = request.get_json()
    token, error = login_user(data)
    if error:
        return jsonify({"error": error}), 401
        
    return jsonify({
        "access_token": token
    })

@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    """
    GET /api/auth/users
    Lists user accounts in the system.
    - Administrators see all users.
    - Managers see only users in their own department.
    """
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())
    
    if role != "Administrator" and role != "Manager":
        return jsonify({"error": "Access denied. Manager or Administrator role required."}), 403
        
    if role == "Administrator":
        # Admins see all users sorted by ID
        users = User.query.order_by(User.id.asc()).all()
    else:
        # Managers see only users in their own department
        manager = User.query.filter_by(id=user_id).first()
        if not manager or not manager.department_id:
            return jsonify([]), 200
        users = User.query.filter_by(department_id=manager.department_id).order_by(User.id.asc()).all()
        
    results = []
    for u in users:
        results.append({
            "id": u.id,
            "employee_id": u.employee_id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "department_name": u.department.name if u.department else "None",
            "is_active": u.is_active
        })
        
    return jsonify(results), 200