# backend/services/upload_service.py
# This service handles local file uploads (validating file types, generating secure unique filenames,
# saving them to the backend storage, and logging them in the database attachments table).

import os
# Import uuid to generate random prefixes for filenames to prevent filename collisions
import uuid
# Import Werkzeug's secure_filename to clean filenames (e.g. preventing path traversal attacks)
from werkzeug.utils import secure_filename

# Import the db instance to log attachments in the database
from extensions import db
# Import the Attachment model
from models.attachment import Attachment

# Define configuration variables (these can be moved to config.py in a production app)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "txt", "xls", "xlsx"}

# Ensure the upload folder directory exists on the system disk
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """
    Checks if the uploaded file's extension is in the list of allowed extensions.
    
    Parameters:
    - filename (str): The name of the file.
    
    Returns:
    - bool: True if allowed, False otherwise.
    """
    # Check if there is a dot in the filename and check if the extension matches (case-insensitive)
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_attachment(file_object, complaint_id, user_id):
    """
    Saves a file uploaded through an HTTP request to the local disk and creates an Attachment record.
    
    Parameters:
    - file_object (FileStorage): The Flask file object from request.files
    - complaint_id (int): The ID of the complaint this file belongs to.
    - user_id (int): The ID of the user uploading the file.
    
    Returns:
    - (Attachment, None) on success.
    - (None, error_message) on failure.
    """
    try:
        # Validate that a file was actually uploaded
        if not file_object or file_object.filename == "":
            return None, "No file uploaded."
            
        # Verify the file type/extension is allowed
        if not allowed_file(file_object.filename):
            return None, "File extension not allowed."
            
        # Sanitize the original filename to prevent path injection
        original_name = secure_filename(file_object.filename)
        
        # Generate a unique filename by prefixing a random UUID hex string
        unique_name = f"{uuid.uuid4().hex}_{original_name}"
        
        # Compute the absolute filepath to write to on disk
        destination_path = os.path.join(UPLOAD_FOLDER, unique_name)
        
        # Save the file to the local directory
        file_object.save(destination_path)
        
        # Create a database record for this upload
        attachment = Attachment(
            complaint_id=complaint_id,
            filename=original_name,
            # We store the unique filename or relative path so it can be fetched/served later
            filepath=unique_name, 
            uploaded_by=user_id
        )
        
        # Add to the session and commit
        db.session.add(attachment)
        db.session.commit()
        
        print(f"File saved: {destination_path} and logged in DB for Complaint {complaint_id}")
        return attachment, None
        
    except Exception as e:
        db.session.rollback()
        return None, str(e)
