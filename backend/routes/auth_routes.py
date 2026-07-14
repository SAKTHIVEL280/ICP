from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.auth_service import register_user, login_user
from models.user import User
from extensions import db

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
    required_fields = ["name", "email", "password", "role"]
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

@auth_bp.route("/users/<int:target_id>", methods=["PUT"])
@jwt_required()
def update_user(target_id):
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Administrator":
        return jsonify({"error": "Access denied. Administrator role required."}), 403
        
    data = request.get_json()
    user = User.query.get(target_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
        
    # Prevent editing the core System Admin ID 1 to avoid locking out the system
    if target_id == 1 and data.get("role") != "Administrator":
        return jsonify({"error": "Cannot change the System Administrator's role."}), 400
        
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.role = data.get("role", user.role)
    user.department_id = data.get("department_id", user.department_id)
    user.is_active = data.get("is_active", user.is_active)
    
    # If a new password is sent, hash it
    password = data.get("password")
    if password and password.strip() != "":
        import bcrypt
        user.password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        
    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

@auth_bp.route("/users/<int:target_id>", methods=["DELETE"])
@jwt_required()
def delete_user(target_id):
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Administrator":
        return jsonify({"error": "Access denied. Administrator role required."}), 403
        
    if target_id == 1:
        return jsonify({"error": "Cannot delete the System Administrator."}), 400
        
    user = User.query.get(target_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
        
    # Check if user has complaints raised or tasks assigned
    from models.complaint import Complaint
    has_raised = Complaint.query.filter_by(employee_id=target_id).first()
    has_assigned = Complaint.query.filter_by(technician_id=target_id).first()
    
    if has_raised or has_assigned:
        return jsonify({"error": "Cannot delete this user because they have complaint tickets linked to their account. Deactivate their status to Inactive instead."}), 400
        
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    PUT /api/auth/profile
    Allows any logged-in user to update their name or change their password.
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided."}), 400
        
    name = data.get("name")
    if name and name.strip() != "":
        user.name = name.strip()
        
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if new_password and new_password.strip() != "":
        if not old_password:
            return jsonify({"error": "Current password is required to change password."}), 400
            
        import bcrypt
        # Verify old password
        if not bcrypt.checkpw(old_password.encode("utf-8"), user.password.encode("utf-8")):
            return jsonify({"error": "Incorrect current password."}), 400
            
        # Hash and save new password
        user.password = bcrypt.hashpw(
            new_password.strip().encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        
    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200