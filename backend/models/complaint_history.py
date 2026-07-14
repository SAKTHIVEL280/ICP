# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the ComplaintHistory model which inherits from db.Model
class ComplaintHistory(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "complaint_history"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each history record

    # Foreign key linking to the complaints table
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False
    ) # ID of the complaint that changed status

    # The previous status of the complaint before this update
    # Can be Null if it's the initial status (e.g. going from nothing to "New")
    old_status = db.Column(
        db.String(20),
        nullable=True
    ) # Previous status state

    # The new status of the complaint after this update
    new_status = db.Column(
        db.String(20),
        nullable=False
    ) # Next status state

    # Foreign key linking to the users table
    # This represents the user who triggered this status change (e.g. technician resolving it, manager assigning it)
    updated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    ) # ID of the user who performed the status update

    # Date and time when the status was updated
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) # Timestamp when the update occurred

    # Relationship back to the User model so we can easily fetch who changed the status
    updater = db.relationship(
        "User",
        backref=db.backref("status_changes", lazy=True)
    ) # Relationship link to access details of the updating user
