from extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    ) # Unique identifier for each user

    name = db.Column(
        db.String(100),
        nullable=False
    ) # Name of the user

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    ) 

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    ) # Role of the user (e.g., admin, employee, etc.)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id")
    ) # Foreign key linking to the departments table

    is_active = db.Column(
        db.Boolean,
        default=True
    ) # Indicates whether the user account is active or not

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    ) 