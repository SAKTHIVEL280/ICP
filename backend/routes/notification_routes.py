# backend/routes/notification_routes.py
# This route file defines endpoints for retrieving and updating user notifications.

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Import our notification service functions
from services.notification_service import (
    get_user_notifications,
    mark_notification_as_read
)

# Create a Flask Blueprint named 'notifications'
notifications_bp = Blueprint("notifications", __name__)

@notifications_bp.route("", methods=["GET"])
@jwt_required()
def index():
    """
    GET /api/notifications
    Retrieves all notifications for the logged-in user, sorted by date (newest first).
    """
    user_id = int(get_jwt_identity())
    
    # Fetch notifications from database
    notifications_list = get_user_notifications(user_id)
    
    # Format database rows to JSON array
    results = []
    for n in notifications_list:
        results.append({
            "id": n.id,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S") if n.created_at else None
        })
        
    return jsonify(results), 200

@notifications_bp.route("/read/<int:notification_id>", methods=["PATCH"])
@jwt_required()
def read(notification_id):
    """
    PATCH /api/notifications/read/<id>
    Marks a specific notification as read.
    """
    user_id = int(get_jwt_identity())
    
    # Mark as read
    notification, error = mark_notification_as_read(notification_id, user_id)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({
        "message": "Notification marked as read successfully",
        "notification_id": notification.id,
        "is_read": notification.is_read
    }), 200
