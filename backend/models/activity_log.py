# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the ActivityLog model which inherits from db.Model
class ActivityLog(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "activity_logs"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each activity log record

    # Foreign key linking to the users table
    # This represents the user who performed the action (e.g. creating/assigning/closing)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    ) # ID of the user who performed the logged action

    # Descriptive string of the action performed (e.g., "Complaint Created", "Technician Assigned")
    action = db.Column(
        db.String(150),
        nullable=False
    ) # Action performed by the user

    # The type of entity affected (e.g., "Complaint", "User", "Category")
    entity_type = db.Column(
        db.String(50),
        nullable=False
    ) # Type of entity that was modified

    # The database ID of the specific entity that was affected/modified
    entity_id = db.Column(
        db.Integer,
        nullable=True
    ) # ID of the specific entity record

    # JSON representation of the properties before the change occurred (nullable)
    old_value = db.Column(
        db.JSON,
        nullable=True
    ) # Prior configuration/data state

    # JSON representation of the properties after the change occurred (nullable)
    new_value = db.Column(
        db.JSON,
        nullable=True
    ) # Post configuration/data state

    # Date and time when the action occurred
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) # Timestamp when the action took place

    # Relationship back to the User model so we can easily fetch details of the user who did the action
    user = db.relationship(
        "User",
        backref=db.backref("activity_logs", lazy=True)
    ) # Relationship link to access details of the actor user
