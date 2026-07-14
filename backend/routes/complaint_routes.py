# backend/routes/complaint_routes.py
# This route file defines all HTTP endpoints related to standard complaint operations,
# comments, and attachment uploads. It uses Flask Blueprints to register routes.

# Import Blueprint, request payload parser, and JSON response utility
from flask import Blueprint, request, jsonify, send_from_directory
# Import JWT decorators to secure these endpoints and extract identity claims
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

# Import our backend service functions which perform the database operations
from services.complaint_service import (
    create_complaint,
    get_complaints,
    get_complaint_by_id,
    update_complaint,
    delete_complaint,
    verify_and_close_complaint,
    create_comment,
    get_comments_by_complaint,
    get_attachments_by_complaint
)
from services.upload_service import save_attachment, UPLOAD_FOLDER
# Import the Category model to fetch categories for form drop-downs
from models.category import Category
from models.department import Department
import os

# Create a Flask Blueprint named 'complaints'
complaints_bp = Blueprint("complaints", __name__)

@complaints_bp.route("", methods=["POST"])
@jwt_required()
def create():
    """
    POST /api/complaints
    Allows an authenticated user to submit a new complaint.
    Automatically assigns the correct department based on the selected category.
    """
    # Extract the user ID of the employee from the JWT token
    user_id = int(get_jwt_identity())
    
    # Parse the incoming JSON body
    data = request.get_json()
    
    # Check if required fields are provided
    if not data or "title" not in data or "description" not in data or "category_id" not in data or "location" not in data:
        return jsonify({"error": "Missing required fields (title, description, category_id, location)"}), 400
        
    # Call the service layer to create the complaint record
    complaint, error = create_complaint(data, user_id)
    if error:
        return jsonify({"error": error}), 400
        
    # Return the newly created complaint details
    return jsonify({
        "message": "Complaint submitted successfully",
        "complaint": {
            "id": complaint.id,
            "complaint_number": complaint.complaint_number,
            "title": complaint.title,
            "status": complaint.status,
            "department_id": complaint.department_id
        }
    }), 201

@complaints_bp.route("", methods=["GET"])
@jwt_required()
def index():
    """
    GET /api/complaints
    Lists complaints. The returned list is filtered by the user's role:
    - Employees see only their own complaints.
    - Technicians see only complaints assigned to them.
    - Managers see all complaints routed to their department.
    - Administrators see all complaints in the system.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    # Call service layer with security claims
    complaints_list = get_complaints(user_id, role)
    
    # Format the list to JSON-serializable dictionaries
    results = []
    for c in complaints_list:
        results.append({
            "id": c.id,
            "complaint_number": c.complaint_number,
            "title": c.title,
            "description": c.description,
            "category": c.category.name if c.category else "Unknown",
            "department": c.department.name if c.department else "Unknown",
            "priority": c.priority,
            "status": c.status,
            "location": c.location,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None,
            "technician": c.technician.name if c.technician else None
        })
        
    return jsonify(results), 200

@complaints_bp.route("/<int:complaint_id>", methods=["GET"])
@jwt_required()
def details(complaint_id):
    """
    GET /api/complaints/<id>
    Fetches the full details of a specific complaint, including its comments, attachments, and history.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    # Fetch details with security checks
    complaint, error = get_complaint_by_id(complaint_id, user_id, role)
    if error:
        return jsonify({"error": error}), 403
        
    # Format comments
    comments_data = []
    for comment in complaint.comments:
        comments_data.append({
            "id": comment.id,
            "comment": comment.comment,
            "author_name": comment.author.name if comment.author else "Unknown",
            "author_role": comment.author.role if comment.author else "Unknown",
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S") if comment.created_at else None
        })
        
    # Format attachments
    attachments_data = []
    for att in complaint.attachments:
        attachments_data.append({
            "id": att.id,
            "filename": att.filename,
            "filepath": att.filepath,
            "uploaded_by_name": att.uploader.name if att.uploader else "Unknown",
            "uploaded_at": att.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if att.uploaded_at else None
        })
        
    # Format status history timeline
    history_data = []
    for hist in complaint.history:
        history_data.append({
            "id": hist.id,
            "old_status": hist.old_status,
            "new_status": hist.new_status,
            "updated_by_name": hist.updater.name if hist.updater else "Unknown",
            "updated_at": hist.updated_at.strftime("%Y-%m-%d %H:%M:%S") if hist.updated_at else None
        })

    return jsonify({
        "id": complaint.id,
        "complaint_number": complaint.complaint_number,
        "title": complaint.title,
        "description": complaint.description,
        "category": complaint.category.name if complaint.category else "Unknown",
        "category_id": complaint.category_id,
        "department": complaint.department.name if complaint.department else "Unknown",
        "priority": complaint.priority,
        "status": complaint.status,
        "location": complaint.location,
        "resolution_note": complaint.resolution_note,
        "created_at": complaint.created_at.strftime("%Y-%m-%d %H:%M:%S") if complaint.created_at else None,
        "updated_at": complaint.updated_at.strftime("%Y-%m-%d %H:%M:%S") if complaint.updated_at else None,
        "closed_at": complaint.closed_at.strftime("%Y-%m-%d %H:%M:%S") if complaint.closed_at else None,
        "technician": {
            "id": complaint.technician.id,
            "name": complaint.technician.name,
            "email": complaint.technician.email
        } if complaint.technician else None,
        "employee": {
            "id": complaint.employee.id,
            "name": complaint.employee.name,
            "email": complaint.employee.email
        } if complaint.employee else None,
        "comments": comments_data,
        "attachments": attachments_data,
        "history": history_data
    }), 200

@complaints_bp.route("/<int:complaint_id>", methods=["PUT"])
@jwt_required()
def update(complaint_id):
    """
    PUT /api/complaints/<id>
    Allows the ticket author to update details (only if status is "New").
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    data = request.get_json()
    
    complaint, error = update_complaint(complaint_id, data, user_id, role)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": "Complaint updated successfully",
        "complaint_id": complaint.id
    }), 200

@complaints_bp.route("/<int:complaint_id>", methods=["DELETE"])
@jwt_required()
def delete(complaint_id):
    """
    DELETE /api/complaints/<id>
    Allows an administrator to delete a complaint ticket.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    success, error = delete_complaint(complaint_id, user_id, role)
    if error:
        return jsonify({"error": error}), 403
        
    return jsonify({"message": "Complaint deleted successfully"}), 200

@complaints_bp.route("/<int:complaint_id>/status", methods=["PATCH"])
@jwt_required()
def verify_status(complaint_id):
    """
    PATCH /api/complaints/<id>/status
    Allows the employee who created the ticket to verify the technician's fix.
    Payload: {"action": "Close"} or {"action": "Reopen"}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or "action" not in data:
        return jsonify({"error": "Missing verification action ('Close' or 'Reopen')"}), 400
        
    complaint, error = verify_and_close_complaint(complaint_id, data["action"], user_id)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": f"Verification submitted: Complaint status is now '{complaint.status}'",
        "status": complaint.status
    }), 200


# --- COMMENTS SUB-ROUTES ---

@complaints_bp.route("/comments", methods=["POST"])
@jwt_required()
def add_comment():
    """
    POST /api/comments
    Submits a comment on a complaint ticket.
    Payload: {"complaint_id": 1, "comment": "This is a comment."}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    if not data or "complaint_id" not in data or "comment" not in data:
        return jsonify({"error": "Missing complaint_id or comment body"}), 400
        
    comment, error = create_comment(data["complaint_id"], user_id, data["comment"])
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": "Comment added successfully",
        "comment": {
            "id": comment.id,
            "comment": comment.comment,
            "author_name": comment.author.name if comment.author else "Unknown",
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S") if comment.created_at else None
        }
    }), 201

@complaints_bp.route("/comments/<int:complaint_id>", methods=["GET"])
@jwt_required()
def list_comments(complaint_id):
    """
    GET /api/comments/<complaint_id>
    Lists all comments for a specific complaint, enforcing permissions.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    comments, error = get_comments_by_complaint(complaint_id, user_id, role)
    if error:
        return jsonify({"error": error}), 403
        
    results = []
    for c in comments:
        results.append({
            "id": c.id,
            "comment": c.comment,
            "author_name": c.author.name if c.author else "Unknown",
            "author_role": c.author.role if c.author else "Unknown",
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else None
        })
        
    return jsonify(results), 200


# --- ATTACHMENTS & UPLOAD SUB-ROUTES ---

@complaints_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    """
    POST /api/upload
    Uploads an attachment file for a complaint.
    Form data fields:
    - file (File)
    - complaint_id (int)
    """
    user_id = int(get_jwt_identity())
    
    # Check if a file is in the request files
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
        
    file = request.files["file"]
    
    # Check if complaint_id is in request form
    complaint_id_str = request.form.get("complaint_id")
    if not complaint_id_str:
        return jsonify({"error": "Missing complaint_id in form data"}), 400
        
    try:
        complaint_id = int(complaint_id_str)
    except ValueError:
        return jsonify({"error": "Invalid complaint_id format (must be integer)"}), 400
        
    # Verify the user has access to this complaint before saving the attachment
    claims = get_jwt()
    role = claims.get("role")
    _, access_error = get_complaint_by_id(complaint_id, user_id, role)
    if access_error:
        return jsonify({"error": f"Access denied to this complaint: {access_error}"}), 403

    # Call upload service to write file and update database
    attachment, error = save_attachment(file, complaint_id, user_id)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": "File uploaded successfully",
        "attachment": {
            "id": attachment.id,
            "filename": attachment.filename,
            "filepath": attachment.filepath
        }
    }), 201

@complaints_bp.route("/attachments/<int:complaint_id>", methods=["GET"])
@jwt_required()
def list_attachments(complaint_id):
    """
    GET /api/attachments/<complaint_id>
    Lists all attachments for a specific complaint.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")
    
    attachments, error = get_attachments_by_complaint(complaint_id, user_id, role)
    if error:
        return jsonify({"error": error}), 403
        
    results = []
    for att in attachments:
        results.append({
            "id": att.id,
            "filename": att.filename,
            "filepath": att.filepath,
            "uploaded_by_name": att.uploader.name if att.uploader else "Unknown",
            "uploaded_at": att.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if att.uploaded_at else None
        })
        
    return jsonify(results), 200

@complaints_bp.route("/uploads/<filename>", methods=["GET"])
def get_uploaded_file(filename):
    """
    GET /api/complaints/uploads/<filename>
    Serves the actual uploaded file from the server uploads directory.
    """
    # Use Flask's send_from_directory to safely serve files and prevent path traversal
    return send_from_directory(UPLOAD_FOLDER, filename)


# --- GENERAL HELPER ROUTES ---

@complaints_bp.route("/categories", methods=["GET"])
def get_categories():
    """
    GET /api/complaints/categories
    Returns all categories with their associated department details.
    Used by the frontend to populate submission forms.
    """
    categories = Category.query.all()
    results = []
    for cat in categories:
        results.append({
            "id": cat.id,
            "name": cat.name,
            "department_id": cat.department_id,
            "department_name": cat.department.name if cat.department else "Unknown"
        })
    return jsonify(results), 200
