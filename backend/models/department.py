from extensions import db

class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    ) # Name of the department

    description = db.Column(
        db.Text
    ) # Description of the department

    users = db.relationship(
        "User",
        backref="department",
        lazy=True
    ) # Relationship to the User model, allowing access to users in this department
    