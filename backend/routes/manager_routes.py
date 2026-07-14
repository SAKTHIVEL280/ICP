# backend/routes/manager_routes.py
# This route file defines endpoints for department managers to assign and reassign technicians,
# and list complaints and technicians under their department.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Import our backend services for complaints
from services.complaint_service import assign_complaint, reassign_complaint, get_complaints
# Import User model to query technicians
from models.user import User

# Create a Flask Blueprint named 'manager'
manager_bp = Blueprint("manager", __name__)

@manager_bp.route("/complaints", methods=["GET"])
@jwt_required()
def department_complaints():
    """
    GET /api/manager/complaints
    Retrieves all complaints belonging to the manager's department.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    # Check authorization: Must be a Manager or Administrator
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied. Manager role required."}), 403
        
    # Get complaints for this manager (get_complaints automatically filters by department for Managers)
    complaints = get_complaints(user_id, role)
    
    results = []
    for c in complaints:
        results.append({
            "id": c.id,
            "complaint_number": c.complaint_number,
            "title": c.title,
            "description": c.description,
            "category": c.category.name if c.category else "Unknown",
            "priority": c.priority,
            "status": c.status,
            "location": c.location,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
            "technician": {
                "id": c.technician.id,
                "name": c.technician.name
            } if c.technician else None,
            "employee": {
                "name": c.employee.name
            } if c.employee else None
        })
        
    return jsonify(results), 200

@manager_bp.route("/assign", methods=["POST"])
@jwt_required()
def assign():
    """
    POST /api/manager/assign
    Assigns a technician to a complaint.
    Payload: {"complaint_id": 1, "technician_id": 4}
    """
    manager_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    # Enforce role restriction
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied. Manager role required."}), 403
        
    data = request.get_json()
    if not data or "complaint_id" not in data or "technician_id" not in data:
        return jsonify({"error": "Missing complaint_id or technician_id"}), 400
        
    # Call service layer to assign the ticket
    complaint, error = assign_complaint(
        complaint_id=data["complaint_id"],
        technician_id=data["technician_id"],
        manager_id=manager_id
    )
    
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": f"Technician successfully assigned to complaint {complaint.complaint_number}.",
        "complaint_id": complaint.id,
        "status": complaint.status
    }), 200

@manager_bp.route("/reassign", methods=["PATCH"])
@jwt_required()
def reassign():
    """
    PATCH /api/manager/reassign
    Reassigns a complaint to a different technician.
    Payload: {"complaint_id": 1, "technician_id": 5}
    """
    manager_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied. Manager role required."}), 403
        
    data = request.get_json()
    if not data or "complaint_id" not in data or "technician_id" not in data:
        return jsonify({"error": "Missing complaint_id or technician_id"}), 400
        
    # Call service layer to reassign
    complaint, error = reassign_complaint(
        complaint_id=data["complaint_id"],
        technician_id=data["technician_id"],
        manager_id=manager_id
    )
    
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": f"Complaint {complaint.complaint_number} has been reassigned successfully.",
        "complaint_id": complaint.id,
        "status": complaint.status
    }), 200

@manager_bp.route("/technicians", methods=["GET"])
@jwt_required()
def get_department_technicians():
    """
    GET /api/manager/technicians
    Lists all active technicians inside the manager's department.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied."}), 403
        
    # Get the manager profile to determine their department
    manager = User.query.filter_by(id=user_id).first()
    if not manager or not manager.department_id:
        return jsonify({"error": "Manager department not configured"}), 400
        
    # Query all users with role 'Technician' who belong to the same department and are active
    technicians = User.query.filter_by(
        department_id=manager.department_id,
        role="Technician",
        is_active=True
    ).all()
    
    results = []
    for tech in technicians:
        results.append({
            "id": tech.id,
            "employee_id": tech.employee_id,
            "name": tech.name,
            "email": tech.email
        })
        
    return jsonify(results), 200
