# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the Attachment model which inherits from db.Model
class Attachment(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "attachments"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each attachment

    # Foreign key linking to the complaint table
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False
    ) # ID of the complaint this file is attached to

    # Original filename of the uploaded file (e.g. error_log.png)
    filename = db.Column(
        db.String(255),
        nullable=False
    ) # Saved filename of the attachment

    # Path where the file is stored on the disk
    filepath = db.Column(
        db.Text,
        nullable=False
    ) # Absolute or relative path to file storage

    # Foreign key linking to the users table
    # This represents the user who uploaded the attachment
    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    ) # ID of the user who uploaded the file

    # Date and time when the file was uploaded
    uploaded_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) # Timestamp when the upload occurred

    # Relationship back to the User model so we can easily fetch who uploaded the attachment
    uploader = db.relationship(
        "User",
        backref=db.backref("attachments", lazy=True)
    ) # Relationship link to access details of the uploader user
