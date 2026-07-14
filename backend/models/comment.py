# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the Comment model which inherits from db.Model
class Comment(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "comments"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each comment

    # Foreign key linking to the complaint table
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False
    ) # ID of the complaint this comment belongs to

    # Foreign key linking to the users table
    # This represents the user (employee, technician, manager, etc.) who wrote the comment
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    ) # ID of the user who posted this comment

    # The actual text content of the comment
    comment = db.Column(
        db.Text,
        nullable=False
    ) # Text content of the comment

    # Date and time when the comment was posted
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) # Timestamp when the comment was created

    # Relationship back to the User model so we can easily fetch who wrote the comment
    author = db.relationship(
        "User",
        backref=db.backref("comments", lazy=True)
    ) # Relationship link to access details of the comment author
