# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the Notification model which inherits from db.Model
class Notification(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "notifications"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each notification

    # Foreign key linking to the users table
    # This represents the user who should receive this notification
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    ) # ID of the user receiving the notification

    # The text message content of the notification
    message = db.Column(
        db.Text,
        nullable=False
    ) # Notification text body

    # Indicates whether the user has read/opened the notification or not
    is_read = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    ) # Read status flag (True = read, False = unread)

    # Date and time when the notification was created
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) # Timestamp when the notification was generated

    # Relationship back to the User model so we can easily fetch details of the receiver
    recipient = db.relationship(
        "User",
        backref=db.backref("notifications", lazy=True, cascade="all, delete-orphan")
    ) # Relationship link to access details of the recipient user
