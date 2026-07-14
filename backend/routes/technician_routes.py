# backend/routes/technician_routes.py
# This route file defines endpoints for technicians to view and update the progress of their tasks.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Import our backend services for complaints
from services.complaint_service import (
    get_complaints,
    accept_complaint,
    start_progress,
    resolve_complaint
)

# Create a Flask Blueprint named 'technician'
technician_bp = Blueprint("technician", __name__)

@technician_bp.route("/tasks", methods=["GET"])
@jwt_required()
def tasks():
    """
    GET /api/technician/tasks
    Retrieves all complaints assigned to the current technician.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    # Enforce technician authorization
    if role != "Technician" and role != "Administrator":
        return jsonify({"error": "Access denied. Technician role required."}), 403
        
    # Get complaints for this technician (get_complaints filters by technician_id automatically)
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
            "employee": {
                "name": c.employee.name,
                "email": c.employee.email
            } if c.employee else None
        })
        
    return jsonify(results), 200

@technician_bp.route("/accept/<int:complaint_id>", methods=["PATCH"])
@jwt_required()
def accept(complaint_id):
    """
    PATCH /api/technician/accept/<id>
    Allows a technician to accept an assigned ticket.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Technician" and role != "Administrator":
        return jsonify({"error": "Access denied. Technician role required."}), 403
        
    complaint, error = accept_complaint(complaint_id, user_id)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": f"Complaint {complaint.complaint_number} has been accepted.",
        "status": complaint.status
    }), 200

@technician_bp.route("/progress/<int:complaint_id>", methods=["PATCH"])
@jwt_required()
def progress(complaint_id):
    """
    PATCH /api/technician/progress/<id>
    Allows a technician to mark an accepted ticket as 'In Progress'.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Technician" and role != "Administrator":
        return jsonify({"error": "Access denied. Technician role required."}), 403
        
    complaint, error = start_progress(complaint_id, user_id)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": f"Complaint {complaint.complaint_number} is now In Progress.",
        "status": complaint.status
    }), 200

@technician_bp.route("/resolve/<int:complaint_id>", methods=["PATCH"])
@jwt_required()
def resolve(complaint_id):
    """
    PATCH /api/technician/resolve/<id>
    Allows a technician to mark a ticket as 'Resolved' and enter resolution notes.
    Payload: {"resolution_note": "Replaced the network cable and verified connectivity."}
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Technician" and role != "Administrator":
        return jsonify({"error": "Access denied. Technician role required."}), 403
        
    data = request.get_json()
    if not data or "resolution_note" not in data:
        return jsonify({"error": "Missing resolution_note in request body"}), 400
        
    complaint, error = resolve_complaint(complaint_id, data["resolution_note"], user_id)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": f"Complaint {complaint.complaint_number} has been marked as Resolved.",
        "status": complaint.status,
        "resolution_note": complaint.resolution_note
    }), 200
