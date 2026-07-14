# Import the db object from extensions.py so we can define our database model
from extensions import db

# Define the Category model which inherits from db.Model
class Category(db.Model):
    # Specify the name of the table in PostgreSQL
    __tablename__ = "categories"

    # Define the primary key column: an integer that auto-increments
    id = db.Column(
        db.Integer,
        primary_key=True
    ) # Unique identifier for each category

    # Define the name of the category (e.g., Laptop, Lighting, Payroll)
    name = db.Column(
        db.String(100),
        nullable=False
    ) # Name of the complaint category

    # Define a foreign key column linking to the departments table.
    # It stores the ID of the department that handles complaints in this category.
    department_id = db.Column(
        db.Integer,
        db.ForeignKey("departments.id"),
        nullable=False
    ) # Foreign key linking this category to its responsible department

    # Define relationship to the Department model
    department = db.relationship(
        "Department",
        backref="categories",
        lazy=True
    )

    # Define a relationship back to the Complaint model.
    # One category can have many complaints associated with it.
    complaints = db.relationship(
        "Complaint",
        backref="category",
        lazy=True
    ) # Allows access to all complaints created under this category
