# backend/services/notification_service.py
# This service file implements the business logic for creating, retrieving, and managing notifications.
# In a real-world app, this could also trigger email sending, WebSockets, or push notifications.

# Import the db instance to perform database operations
from extensions import db
# Import the Notification model to interact with the notifications table
from models.notification import Notification

def create_notification(user_id, message):
    """
    Creates a new notification record in the database for a specific user.
    
    Parameters:
    - user_id (int): The database ID of the user who should receive this notification.
    - message (str): The body text of the notification.
    
    Returns:
    - Notification: The newly created Notification object.
    """
    try:
        # Create an instance of the Notification model
        notification = Notification(
            user_id=user_id,
            message=message,
            is_read=False # Set default read status to False
        )
        
        # Add the notification to the database session
        db.session.add(notification)
        
        # Commit the transaction so it is saved to PostgreSQL immediately
        db.session.commit()
        
        print(f"Notification created for User ID {user_id}: {message}")
        return notification
    except Exception as e:
        # If anything goes wrong, roll back any uncommitted changes to keep the DB in a clean state
        db.session.rollback()
        print(f"Error creating notification: {e}")
        return None

def get_user_notifications(user_id):
    """
    Retrieves all notifications for a specific user, sorted by the newest first.
    
    Parameters:
    - user_id (int): The database ID of the user.
    
    Returns:
    - List[Notification]: A list of Notification objects belonging to the user.
    """
    # Query notifications where the user_id matches and order them descending by created_at
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

def mark_notification_as_read(notification_id, user_id):
    """
    Marks a specific notification as read, ensuring it belongs to the requesting user for security.
    
    Parameters:
    - notification_id (int): The ID of the notification to update.
    - user_id (int): The ID of the user who owns this notification.
    
    Returns:
    - (Notification, None) on success.
    - (None, error_message) on failure.
    """
    try:
        # Query the database for a notification with the specified ID and belonging to the user
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        
        # If no matching notification is found, return an error message
        if not notification:
            return None, "Notification not found or access denied."
            
        # Update the is_read flag to True
        notification.is_read = True
        
        # Commit the database changes
        db.session.commit()
        
        return notification, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)
