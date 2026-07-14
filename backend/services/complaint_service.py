# backend/services/complaint_service.py
# This service file encapsulates all core business logic related to the complaint lifecycle,
# including submission, auto-assignment of departments, updates, deletions, technician assignments,
# technician state changes, and employee verification/closure.

# Import Python's datetime module to handle timestamps for creation, updates, and closure
from datetime import datetime
# Import Python's random module to generate a unique suffix for complaint numbers
import random

# Import the database object to handle transactions and session queries
from extensions import db
# Import all database models involved in the complaint workflow
from models.complaint import Complaint
from models.category import Category
from models.user import User
from models.complaint_history import ComplaintHistory
from models.activity_log import ActivityLog
from models.comment import Comment
from models.attachment import Attachment
# Import the notification helper to trigger real-time updates for relevant users
from services.notification_service import create_notification

def generate_complaint_number():
    """
    Generates a unique complaint ticket number formatted as: COMP-YYYYMMDD-XXXX.
    For example: COMP-20260714-4829
    
    Returns:
    - str: A unique complaint number.
    """
    # Get the current date in YYYYMMDD format
    date_str = datetime.now().strftime("%Y%m%d")
    # Generate a random 4-digit number to avoid collisions
    random_suffix = random.randint(1000, 9999)
    # Combine them into the final ticket identifier
    return f"COMP-{date_str}-{random_suffix}"

def create_complaint(data, employee_id):
    """
    Creates a new complaint ticket in the database.
    
    Parameters:
    - data (dict): The request payload containing:
      - title (str)
      - description (str)
      - category_id (int)
      - location (str)
      - priority (str) - optional
    - employee_id (int): The ID of the employee raising the issue.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        # Check if the category exists in the database
        category = Category.query.filter_by(id=data["category_id"]).first()
        if not category:
            return None, "Selected category does not exist."
            
        # Get the department assigned to this category
        # This fulfills the "Automatic Department Assignment" requirement
        department_id = category.department_id
        
        # Generate a unique complaint ticket number
        complaint_num = generate_complaint_number()
        
        # Create a new instance of the Complaint model
        complaint = Complaint(
            complaint_number=complaint_num,
            title=data["title"],
            description=data["description"],
            category_id=data["category_id"],
            department_id=department_id,
            employee_id=employee_id,
            technician_id=None, # Newly created complaints are not assigned to any technician
            priority=data.get("priority", "Low"), # Default priority is Low if not specified
            status="New", # Newly created complaints are in "New" state
            location=data["location"],
            resolution_note=None
        )
        
        # Add to the database session
        db.session.add(complaint)
        # Flush the session to assign an ID to the complaint record without committing yet
        db.session.flush()
        
        # 1. Log this state transition in the Complaint History table
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=None,
            new_status="New",
            updated_by=employee_id
        )
        db.session.add(history)
        
        # 2. Log this in the general System Activity Logs table
        activity = ActivityLog(
            user_id=employee_id,
            action="Complaint Created",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value=None,
            new_value={"status": "New", "complaint_number": complaint_num}
        )
        db.session.add(activity)
        
        # Commit the transaction to save all three inserts (complaint, history, activity) together
        db.session.commit()
        
        # 3. Notify the managers of the responsible department
        managers = User.query.filter_by(department_id=department_id, role="Manager").all()
        for manager in managers:
            create_notification(
                user_id=manager.id,
                message=f"New complaint {complaint_num} has been submitted for your department."
            )
            
        return complaint, None
        
    except Exception as e:
        # If any step fails, roll back all DB changes in this transaction
        db.session.rollback()
        return None, str(e)

def get_complaints(user_id, role, department_id=None):
    """
    Retrieves the list of complaints filtered by the user's role and department constraints.
    
    Parameters:
    - user_id (int): The current authenticated user's database ID.
    - role (str): The current user's role (Employee, Technician, Manager, Administrator).
    - department_id (int): The department ID of the user (mainly for Managers/Technicians).
    
    Returns:
    - List[Complaint]: The list of matching Complaint objects.
    """
    # Standard query for complaints
    query = Complaint.query

    # Rule-Based Filtering:
    if role == "Employee":
        # Employees can only view their own complaints
        return query.filter_by(employee_id=user_id).order_by(Complaint.created_at.desc()).all()
        
    elif role == "Technician":
        # Technicians can only view complaints assigned to them
        return query.filter_by(technician_id=user_id).order_by(Complaint.created_at.desc()).all()
        
    elif role == "Manager":
        # Managers can view all complaints routed to their department
        # We look up the department ID of the manager
        manager = User.query.filter_by(id=user_id).first()
        if manager and manager.department_id:
            return query.filter_by(department_id=manager.department_id).order_by(Complaint.created_at.desc()).all()
        return []
        
    elif role == "Administrator":
        # Administrators can view all complaints across the system
        return query.order_by(Complaint.created_at.desc()).all()
        
    return []

def get_complaint_by_id(complaint_id, user_id, role):
    """
    Retrieves a single complaint details by ID, enforcing security permissions.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - user_id (int): The ID of the authenticated user.
    - role (str): The role of the user.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    # Fetch the complaint from database
    complaint = Complaint.query.filter_by(id=complaint_id).first()
    if not complaint:
        return None, "Complaint not found."
        
    # Check permissions depending on the role:
    if role == "Employee" and complaint.employee_id != user_id:
        return None, "Access denied. You do not own this complaint."
        
    elif role == "Technician" and complaint.technician_id != user_id:
        # A technician must be assigned to view it
        return None, "Access denied. This complaint is not assigned to you."
        
    elif role == "Manager":
        # Manager must belong to the department of the complaint
        manager = User.query.filter_by(id=user_id).first()
        if not manager or complaint.department_id != manager.department_id:
            return None, "Access denied. This complaint belongs to another department."
            
    # Admins have full read access to all complaints
    return complaint, None

def update_complaint(complaint_id, data, user_id, role):
    """
    Updates the editable details of a complaint. 
    Can only be performed if the complaint is still in "New" state, or by an Admin.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - data (dict): The fields to modify (title, description, category_id, location, priority).
    - user_id (int): The editor's ID.
    - role (str): The editor's role.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        # Enforce edit constraints: Employees can only edit their own complaints if the status is "New"
        if role == "Employee":
            if complaint.employee_id != user_id:
                return None, "Access denied. You do not own this complaint."
            if complaint.status != "New":
                return None, "Cannot edit complaint once it has been processed."
        elif role != "Administrator" and role != "Manager":
            return None, "Access denied."
            
        # Store a snapshot of the current state for the audit log
        old_val = {
            "title": complaint.title,
            "description": complaint.description,
            "category_id": complaint.category_id,
            "location": complaint.location,
            "priority": complaint.priority,
            "department_id": complaint.department_id
        }
        
        # Update details:
        if "title" in data:
            complaint.title = data["title"]
        if "description" in data:
            complaint.description = data["description"]
        if "location" in data:
            complaint.location = data["location"]
        if "priority" in data:
            complaint.priority = data["priority"]
            
        # Handle category changes, updating the responsible department automatically
        if "category_id" in data:
            category = Category.query.filter_by(id=data["category_id"]).first()
            if not category:
                return None, "Category not found."
            complaint.category_id = data["category_id"]
            complaint.department_id = category.department_id
            
        new_val = {
            "title": complaint.title,
            "description": complaint.description,
            "category_id": complaint.category_id,
            "location": complaint.location,
            "priority": complaint.priority,
            "department_id": complaint.department_id
        }
        
        # Log this edit operation in system activities
        activity = ActivityLog(
            user_id=user_id,
            action="Complaint Updated",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value=old_val,
            new_value=new_val
        )
        db.session.add(activity)
        
        # Commit the transaction
        db.session.commit()
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def delete_complaint(complaint_id, user_id, role):
    """
    Deletes a complaint ticket. Only administrators are allowed to delete tickets.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - user_id (int): The ID of the user performing deletion.
    - role (str): The role of the user performing deletion.
    
    Returns:
    - (True, None) on success.
    - (None, error_message) on failure.
    """
    try:
        if role != "Administrator":
            return None, "Access denied. Only administrators can delete complaints."
            
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        # Log the deletion event before removal
        activity = ActivityLog(
            user_id=user_id,
            action="Complaint Deleted",
            entity_type="Complaint",
            entity_id=complaint_id,
            old_value={"complaint_number": complaint.complaint_number, "title": complaint.title},
            new_value=None
        )
        db.session.add(activity)
        
        # Delete the complaint. Related comments, history, and attachments will cascade delete.
        db.session.delete(complaint)
        db.session.commit()
        
        return True, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def assign_complaint(complaint_id, technician_id, manager_id):
    """
    Assigns a technician to a complaint ticket. Sets the status to "Assigned".
    Can only be done by Managers (of that department) or Administrators.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - technician_id (int): The ID of the technician to assign.
    - manager_id (int): The ID of the manager assigning the ticket.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        # Check if the complaint exists
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        # Check if the technician exists and has the correct role
        technician = User.query.filter_by(id=technician_id, role="Technician").first()
        if not technician:
            return None, "Selected user is not a valid technician."
            
        # Validate that the technician belongs to the same department as the complaint
        if technician.department_id != complaint.department_id:
            return None, "Technician does not belong to the responsible department."
            
        # Keep track of old state
        old_status = complaint.status
        
        # Update complaint properties
        complaint.technician_id = technician_id
        complaint.status = "Assigned"
        
        # Log status transition history
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status="Assigned",
            updated_by=manager_id
        )
        db.session.add(history)
        
        # Log system activity
        activity = ActivityLog(
            user_id=manager_id,
            action="Technician Assigned",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value={"status": old_status, "technician_id": None},
            new_value={"status": "Assigned", "technician_id": technician_id}
        )
        db.session.add(activity)
        
        # Save changes
        db.session.commit()
        
        # Notify the assigned technician
        create_notification(
            user_id=technician_id,
            message=f"You have been assigned to Complaint {complaint.complaint_number}: '{complaint.title}'."
        )
        
        # Notify the employee who created the ticket
        create_notification(
            user_id=complaint.employee_id,
            message=f"Your complaint {complaint.complaint_number} has been assigned to Technician {technician.name}."
        )
        
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def reassign_complaint(complaint_id, technician_id, manager_id):
    """
    Reassigns a complaint ticket to a different technician. Keeps status as "Assigned".
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - technician_id (int): The ID of the new technician.
    - manager_id (int): The ID of the manager performing the reassignment.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        # Ensure the ticket is already assigned
        if not complaint.technician_id:
            return None, "Complaint is not currently assigned. Use assign instead."
            
        technician = User.query.filter_by(id=technician_id, role="Technician").first()
        if not technician:
            return None, "Selected user is not a valid technician."
            
        if technician.department_id != complaint.department_id:
            return None, "Technician does not belong to the responsible department."
            
        old_tech_id = complaint.technician_id
        complaint.technician_id = technician_id
        complaint.status = "Assigned" # Reset status to Assigned in case they were in progress
        
        # Log status transition history
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=complaint.status,
            new_status="Assigned",
            updated_by=manager_id
        )
        db.session.add(history)
        
        # Log system activity
        activity = ActivityLog(
            user_id=manager_id,
            action="Technician Reassigned",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value={"technician_id": old_tech_id},
            new_value={"technician_id": technician_id}
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Notify the new technician
        create_notification(
            user_id=technician_id,
            message=f"You have been reassigned to Complaint {complaint.complaint_number}."
        )
        
        # Notify the old technician that they've been unassigned
        create_notification(
            user_id=old_tech_id,
            message=f"You have been unassigned from Complaint {complaint.complaint_number}."
        )
        
        # Notify the employee
        create_notification(
            user_id=complaint.employee_id,
            message=f"Your complaint {complaint.complaint_number} has been reassigned to Technician {technician.name}."
        )
        
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def accept_complaint(complaint_id, technician_id):
    """
    Allows an assigned technician to accept the work. Updates status to "Accepted".
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - technician_id (int): The ID of the technician accepting the complaint.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        # Security check: Ensure only the assigned technician can accept it
        if complaint.technician_id != technician_id:
            return None, "Access denied. You are not assigned to this complaint."
            
        # Transition rule: Can only accept from "Assigned" status
        if complaint.status != "Assigned":
            return None, f"Cannot accept complaint in status '{complaint.status}'."
            
        old_status = complaint.status
        complaint.status = "Accepted"
        
        # Log history
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status="Accepted",
            updated_by=technician_id
        )
        db.session.add(history)
        
        # Log activity
        activity = ActivityLog(
            user_id=technician_id,
            action="Complaint Accepted",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value={"status": old_status},
            new_value={"status": "Accepted"}
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Notify employee
        create_notification(
            user_id=complaint.employee_id,
            message=f"Technician has accepted your complaint {complaint.complaint_number} and will begin work shortly."
        )
        
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def start_progress(complaint_id, technician_id):
    """
    Updates the complaint status to "In Progress".
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - technician_id (int): The ID of the technician working on it.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        if complaint.technician_id != technician_id:
            return None, "Access denied. You are not assigned to this complaint."
            
        # Transition rule: Can start progress from "Accepted"
        if complaint.status != "Accepted":
            return None, f"Cannot start progress for complaint in status '{complaint.status}'."
            
        old_status = complaint.status
        complaint.status = "In Progress"
        
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status="In Progress",
            updated_by=technician_id
        )
        db.session.add(history)
        
        activity = ActivityLog(
            user_id=technician_id,
            action="Work In Progress",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value={"status": old_status},
            new_value={"status": "In Progress"}
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Notify employee
        create_notification(
            user_id=complaint.employee_id,
            message=f"Your complaint {complaint.complaint_number} is now 'In Progress'."
        )
        
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def resolve_complaint(complaint_id, resolution_note, technician_id):
    """
    Marks the complaint as "Resolved" and saves the technician's resolution explanation.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - resolution_note (str): Details of how the issue was fixed.
    - technician_id (int): The ID of the technician.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        if complaint.technician_id != technician_id:
            return None, "Access denied. You are not assigned to this complaint."
            
        # Transition rule: Can only resolve from "In Progress"
        if complaint.status != "In Progress":
            return None, f"Cannot resolve complaint in status '{complaint.status}'."
            
        if not resolution_note or resolution_note.strip() == "":
            return None, "Resolution notes are required to resolve a complaint."
            
        old_status = complaint.status
        complaint.status = "Resolved"
        complaint.resolution_note = resolution_note
        
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status="Resolved",
            updated_by=technician_id
        )
        db.session.add(history)
        
        activity = ActivityLog(
            user_id=technician_id,
            action="Complaint Resolved",
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value={"status": old_status},
            new_value={"status": "Resolved", "resolution_note": resolution_note}
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Notify employee: they must now verify the fix
        create_notification(
            user_id=complaint.employee_id,
            message=f"Your complaint {complaint.complaint_number} is marked as Resolved. Please review and verify to close."
        )
        
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def verify_and_close_complaint(complaint_id, action, employee_id):
    """
    Allows the employee who created the ticket to verify the work.
    They can choose to:
    - Approve/Close the ticket -> Status becomes "Closed", closed_at timestamp is saved.
    - Reject -> Status goes back to "In Progress" so the technician can fix it further.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - action (str): "Close" or "Reopen".
    - employee_id (int): The employee's ID.
    
    Returns:
    - (Complaint, None) on success.
    - (None, error_message) on failure.
    """
    try:
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        # Ensure only the employee who created this complaint can verify it
        if complaint.employee_id != employee_id:
            return None, "Access denied. Only the author of this complaint can verify resolution."
            
        # Can only verify when status is "Resolved"
        if complaint.status != "Resolved":
            return None, "Cannot perform verification. The complaint is not in a 'Resolved' state."
            
        old_status = complaint.status
        
        if action == "Close":
            complaint.status = "Closed"
            complaint.closed_at = datetime.now()
            action_desc = "Complaint Closed"
        elif action == "Reopen":
            complaint.status = "In Progress" # Put it back to in progress
            action_desc = "Complaint Reopened"
        else:
            return None, "Invalid verification action. Must be 'Close' or 'Reopen'."
            
        # Log history
        history = ComplaintHistory(
            complaint_id=complaint.id,
            old_status=old_status,
            new_status=complaint.status,
            updated_by=employee_id
        )
        db.session.add(history)
        
        # Log activity
        activity = ActivityLog(
            user_id=employee_id,
            action=action_desc,
            entity_type="Complaint",
            entity_id=complaint.id,
            old_value={"status": old_status},
            new_value={"status": complaint.status}
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Notify technician and department managers
        if complaint.technician_id:
            if action == "Close":
                create_notification(
                    user_id=complaint.technician_id,
                    message=f"The employee has verified and Closed Complaint {complaint.complaint_number}."
                )
            else:
                create_notification(
                    user_id=complaint.technician_id,
                    message=f"The employee rejected the resolution for {complaint.complaint_number}. The ticket is reopened."
                )
                
        return complaint, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def create_comment(complaint_id, user_id, comment_text):
    """
    Creates a new comment for a complaint.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - user_id (int): The ID of the user posting the comment.
    - comment_text (str): The body text of the comment.
    
    Returns:
    - (Comment, None) on success.
    - (None, error_message) on failure.
    """
    try:
        # Check if the complaint exists
        complaint = Complaint.query.filter_by(id=complaint_id).first()
        if not complaint:
            return None, "Complaint not found."
            
        if not comment_text or comment_text.strip() == "":
            return None, "Comment text cannot be empty."
            
        # Create comment database object
        comment = Comment(
            complaint_id=complaint_id,
            user_id=user_id,
            comment=comment_text
        )
        
        # Add and save
        db.session.add(comment)
        
        # Log this activity
        activity = ActivityLog(
            user_id=user_id,
            action="Comment Added",
            entity_type="Complaint",
            entity_id=complaint_id,
            old_value=None,
            new_value={"comment_preview": comment_text[:50]}
        )
        db.session.add(activity)
        
        db.session.commit()
        
        # Notify other key users involved in the ticket:
        # If the commenter is the employee, notify the assigned technician (if any)
        # If the commenter is the technician, notify the employee
        if user_id == complaint.employee_id and complaint.technician_id:
            create_notification(
                user_id=complaint.technician_id,
                message=f"New comment on Complaint {complaint.complaint_number} by the employee."
            )
        elif complaint.technician_id and user_id == complaint.technician_id:
            create_notification(
                user_id=complaint.employee_id,
                message=f"New comment on Complaint {complaint.complaint_number} by the technician."
            )
            
        return comment, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def get_comments_by_complaint(complaint_id, user_id, role):
    """
    Retrieves all comments for a complaint, verifying access rights.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - user_id (int): The ID of the user requesting comments.
    - role (str): The role of the user.
    
    Returns:
    - (List[Comment], None) on success.
    - (None, error_message) on failure.
    """
    # Verify access to the complaint first using our helper
    complaint, err = get_complaint_by_id(complaint_id, user_id, role)
    if err:
        return None, err
        
    # Return comments sorted ascending by created_at (oldest first, like a chat timeline)
    comments = Comment.query.filter_by(complaint_id=complaint_id).order_by(Comment.created_at.asc()).all()
    return comments, None

def get_attachments_by_complaint(complaint_id, user_id, role):
    """
    Retrieves all attachments for a complaint, verifying access rights.
    
    Parameters:
    - complaint_id (int): The ID of the complaint.
    - user_id (int): The ID of the user requesting attachments.
    - role (str): The role of the user.
    
    Returns:
    - (List[Attachment], None) on success.
    - (None, error_message) on failure.
    """
    complaint, err = get_complaint_by_id(complaint_id, user_id, role)
    if err:
        return None, err
        
    attachments = Attachment.query.filter_by(complaint_id=complaint_id).order_by(Attachment.uploaded_at.desc()).all()
    return attachments, None
