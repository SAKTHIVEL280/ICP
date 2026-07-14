# seed.py
# This script is used to populate our PostgreSQL database with initial data (departments, categories, and default users).
# It allows us to immediately test the application with ready-made login credentials.

# Import the Flask application instance from app.py
from app import app
# Import the db object from extensions.py so we can execute database sessions
from extensions import db
# Import all database models we need to insert data into
from models.department import Department
from models.category import Category
from models.user import User

# Import bcrypt to hash our default user passwords
import bcrypt

def seed_database():
    # We must run database operations within the Flask application context so SQLAlchemy knows which database to connect to.
    with app.app_context():
        print("Starting database seeding...")

        # 1. Clear existing categories, users, and departments to start fresh (useful for testing)
        # We delete in order of dependencies (child tables first, then parent tables)
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.query(Department).delete()
        db.session.commit()
        print("Cleared old data.")

        # 2. Define Departments and their Categories
        # This matches the design specifications in INTERNAL COMPLAINT PORTAL.md
        departments_data = {
            "IT Support": [
                "Computer",
                "Laptop",
                "Printer",
                "Software Installation",
                "Network",
                "Internet",
                "Email"
            ],
            "Facilities": [
                "Air Conditioner",
                "Lighting",
                "Furniture",
                "Water Supply",
                "Washroom",
                "Meeting Room"
            ],
            "Maintenance": [
                "Machine Failure",
                "Generator",
                "Motor",
                "Conveyor",
                "Sensor"
            ],
            "Human Resources": [
                "Payroll",
                "Attendance",
                "ID Card",
                "Access Card"
            ],
            "Safety": [
                "Fire Hazard",
                "Electrical Hazard",
                "Emergency Equipment",
                "Unsafe Workplace"
            ]
        }

        # Dict to store the Department database objects after they are created, keyed by their name.
        # This makes it easy to assign the correct department_id to categories and users.
        created_departments = {}

        # Loop through the department names and lists of categories
        for dept_name, categories_list in departments_data.items():
            # Create a Department database object
            dept = Department(
                name=dept_name,
                description=f"Handles issues related to {dept_name}"
            )
            # Add to the database session
            db.session.add(dept)
            # Commit the session to generate the auto-incrementing ID for the department
            db.session.commit()
            created_departments[dept_name] = dept
            print(f"Created Department: {dept_name} (ID: {dept.id})")

            # Loop through each category in this department and create Category objects
            for cat_name in categories_list:
                cat = Category(
                    name=cat_name,
                    department_id=dept.id
                )
                db.session.add(cat)
            db.session.commit()
            print(f"  -> Added {len(categories_list)} categories for {dept_name}")

        # 3. Create Default Users for testing
        # We define a helper function to quickly hash passwords and create a user
        def create_default_user(emp_id, name, email, raw_password, role, dept_name=None):
            # Hash the raw password using bcrypt
            hashed_pwd = bcrypt.hashpw(
                raw_password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # Get the department ID if a department name is provided
            dept_id = None
            if dept_name and dept_name in created_departments:
                dept_id = created_departments[dept_name].id

            # Create User object
            user = User(
                employee_id=emp_id,
                name=name,
                email=email,
                password=hashed_pwd,
                role=role,
                department_id=dept_id
            )
            db.session.add(user)
            db.session.commit()
            print(f"Created User: {name} | Role: {role} | Email: {email} | Password: {raw_password}")

        # Define default users
        # Only seed the primary System Administrator account (as requested by user)
        # Other users will be created dynamically via the User Management panel.
        create_default_user("EMP001", "System Administrator", "admin@company.com", "Admin@123", "Administrator")

        print("Database seeding completed successfully!")

# If this file is run directly (python seed.py), run the seed_database function
if __name__ == "__main__":
    seed_database()
