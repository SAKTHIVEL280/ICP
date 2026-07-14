# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the Complaint model which inherits from db.Model
class Complaint(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "complaints"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each complaint

    # Unique human-readable complaint ticket number (e.g. COMP-20231024-001)
    complaint_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    ) # Unique identifier ticket number for reference

    # Title of the complaint
    title = db.Column(
        db.String(200),
        nullable=False
    ) # Short summary of the issue

    # Detailed description of the complaint
    description = db.Column(
        db.Text,
        nullable=False
    ) # Detailed explanation of what is wrong

    # Foreign key linking to the category table
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    ) # Category of the issue (e.g. Printer, Lightbulb, Payroll)

    # Foreign key linking to the department table (e.g. IT support, Facilities)
    # This represents the department responsible for resolving this complaint
    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    ) # Department responsible for resolving the complaint

    # Foreign key linking to the user who raised/created this complaint (the employee)
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    ) # User ID of the employee who reported the problem

    # Foreign key linking to the user assigned to resolve this complaint (the technician)
    # It is nullable because a new complaint is not assigned to any technician initially.
    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    ) # User ID of the technician assigned to the ticket, if any

    # Priority of the complaint (Low, Medium, High, Critical)
    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Low"
    ) # Severity of the complaint

    # Status of the complaint (New, Assigned, Accepted, In Progress, Resolved, Employee Verification, Closed, Rejected)
    status = db.Column(
        db.String(20),
        nullable=False,
        default="New"
    ) # Current stage in the complaint lifecycle

    # Physical location where the issue occurred (e.g. Block A, Room 302)
    location = db.Column(
        db.String(150),
        nullable=False
    ) # Where the issue is located

    # Notes added by the technician explaining how the issue was resolved
    resolution_note = db.Column(
        db.Text,
        nullable=True
    ) # Explanation of the final resolution

    # Date and time when the complaint was created
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) # Creation timestamp

    # Date and time when the complaint was last updated
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    ) # Last modification timestamp

    # Date and time when the complaint was closed (verified by employee or finalized)
    closed_at = db.Column(
        db.DateTime,
        nullable=True
    ) # Closing timestamp

    # Relationships:
    # 1. A complaint can have many comments
    comments = db.relationship(
        "Comment",
        backref="complaint",
        lazy=True,
        cascade="all, delete-orphan"
    ) # Link to comments on this complaint

    # 2. A complaint can have many attachments
    attachments = db.relationship(
        "Attachment",
        backref="complaint",
        lazy=True,
        cascade="all, delete-orphan"
    ) # Link to uploaded files/images for this complaint

    # 3. A complaint has a history of status changes
    history = db.relationship(
        "ComplaintHistory",
        backref="complaint",
        lazy=True,
        cascade="all, delete-orphan"
    ) # Link to state transition logs for this complaint

    # 4. A complaint is assigned to a department
    department = db.relationship(
        "Department",
        foreign_keys=[department_id],
        backref="complaints",
        lazy=True
    )

    # 5. A complaint is raised by an employee (User)
    employee = db.relationship(
        "User",
        foreign_keys=[employee_id],
        backref="raised_complaints",
        lazy=True
    )

    # 6. A complaint can be assigned to a technician (User)
    technician = db.relationship(
        "User",
        foreign_keys=[technician_id],
        backref="assigned_complaints",
        lazy=True
    )
