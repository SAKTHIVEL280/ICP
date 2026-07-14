# backend/routes/report_routes.py
# This route file defines endpoints for department managers and admins to view statistics and charts.

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt

# Import report service helper functions
from services.report_service import (
    get_complaint_summary,
    get_complaints_by_department,
    get_complaints_by_category,
    get_complaints_by_priority,
    get_monthly_complaints
)

# Create a Flask Blueprint named 'reports'
reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """
    GET /api/reports/summary
    Retrieves status count summary of complaints.
    Authorized roles: Manager, Administrator.
    """
    claims = get_jwt()
    role = claims.get("role")
    
    # Check permissions
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied. Reports are restricted to managers and administrators."}), 403
        
    data = get_complaint_summary()
    return jsonify(data), 200

@reports_bp.route("/department", methods=["GET"])
@jwt_required()
def department():
    """
    GET /api/reports/department
    Retrieves complaint counts grouped by department.
    Authorized roles: Manager, Administrator.
    """
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied."}), 403
        
    data = get_complaints_by_department()
    return jsonify(data), 200

@reports_bp.route("/category", methods=["GET"])
@jwt_required()
def category():
    """
    GET /api/reports/category
    Retrieves complaint counts grouped by category.
    """
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied."}), 403
        
    data = get_complaints_by_category()
    return jsonify(data), 200

@reports_bp.route("/priority", methods=["GET"])
@jwt_required()
def priority():
    """
    GET /api/reports/priority
    Retrieves complaint counts grouped by priority level.
    """
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied."}), 403
        
    data = get_complaints_by_priority()
    return jsonify(data), 200

@reports_bp.route("/monthly", methods=["GET"])
@jwt_required()
def monthly():
    """
    GET /api/reports/monthly
    Retrieves complaint counts grouped by month (chronological trends).
    """
    claims = get_jwt()
    role = claims.get("role")
    
    if role != "Manager" and role != "Administrator":
        return jsonify({"error": "Access denied."}), 403
        
    data = get_monthly_complaints()
    return jsonify(data), 200
