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

        # 1. Clear existing data in correct dependency order (child tables first)
        from models.complaint import Complaint
        from models.comment import Comment
        from models.attachment import Attachment
        from models.complaint_history import ComplaintHistory
        from models.notification import Notification
        from models.activity_log import ActivityLog

        db.session.query(Comment).delete()
        db.session.query(Attachment).delete()
        db.session.query(ComplaintHistory).delete()
        db.session.query(Complaint).delete()
        db.session.query(Notification).delete()
        db.session.query(ActivityLog).delete()
        db.session.query(Category).delete()
        db.session.query(User).delete()
        db.session.query(Department).delete()

        # Reset PostgreSQL serial sequence counters back to 1
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS departments_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS categories_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS complaints_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS comments_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS attachments_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS complaint_history_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS notifications_id_seq RESTART WITH 1;"))
        db.session.execute(db.text("ALTER SEQUENCE IF EXISTS activity_logs_id_seq RESTART WITH 1;"))

        db.session.commit()
        print("Cleared old data successfully.")

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
        created_categories = {}

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
                created_categories[cat_name] = cat
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
            return user

        # Define default users
        admin_user = create_default_user("EMP001", "System Administrator", "admin@compamy.com", "Admin@123", "Administrator")
        sakthivel = create_default_user("EMP002", "Sakthivel", "sakthivel@company.com", "Sakthivel@123", "Employee", "Human Resources")
        praveen = create_default_user("EMP003", "Praveen", "praveen@company.com", "Praveen@123", "Manager", "IT Support")
        pavithran = create_default_user("EMP004", "Pavithran", "pavithran@company.com", "Pavithran@123", "Technician", "IT Support")
        naveen = create_default_user("EMP005", "Naveen", "naveen@company.com", "Naveen@123", "Manager", "Facilities")
        lokesh = create_default_user("EMP006", "Lokesh", "lokesh@company.com", "Lokesh@123", "Technician", "Facilities")
        harish = create_default_user("EMP007", "Harish", "harish@company.com", "Harish@123", "Employee", "IT Support")

        # 4. Create workflow scenario tickets
        from models.complaint import Complaint
        from models.comment import Comment
        from models.complaint_history import ComplaintHistory
        from datetime import datetime, timedelta

        # Scenario 1: IT software installation ticket - fully resolved
        c1 = Complaint(
            complaint_number="COM001",
            title="Request for Python and IDE Installation",
            description="Need Python 3.11 and VS Code installed on my workstation for data analysis scripts.",
            category_id=created_categories["Software Installation"].id,
            department_id=created_departments["IT Support"].id,
            employee_id=sakthivel.id,
            technician_id=pavithran.id,
            priority="Medium",
            status="Resolved",
            location="Room 204, HR wing",
            resolution_note="Python 3.11 and VS Code IDE installed. Environment variables configured successfully.",
            created_at=datetime.utcnow() - timedelta(days=2),
            updated_at=datetime.utcnow() - timedelta(hours=4)
        )
        db.session.add(c1)
        db.session.commit()

        # History log for c1
        h1_1 = ComplaintHistory(complaint_id=c1.id, old_status="New", new_status="Assigned", updated_by=praveen.id, updated_at=datetime.utcnow() - timedelta(days=1, hours=20))
        h1_2 = ComplaintHistory(complaint_id=c1.id, old_status="Assigned", new_status="Accepted", updated_by=pavithran.id, updated_at=datetime.utcnow() - timedelta(days=1, hours=18))
        h1_3 = ComplaintHistory(complaint_id=c1.id, old_status="Accepted", new_status="In Progress", updated_by=pavithran.id, updated_at=datetime.utcnow() - timedelta(days=1, hours=17))
        h1_4 = ComplaintHistory(complaint_id=c1.id, old_status="In Progress", new_status="Resolved", updated_by=pavithran.id, updated_at=datetime.utcnow() - timedelta(hours=4))
        db.session.add_all([h1_1, h1_2, h1_3, h1_4])

        # Comments for c1
        comm1_1 = Comment(complaint_id=c1.id, user_id=sakthivel.id, comment="Please install the packages soon, needed for a project today.", created_at=datetime.utcnow() - timedelta(days=1, hours=22))
        comm1_2 = Comment(complaint_id=c1.id, user_id=pavithran.id, comment="Starting installation now.", created_at=datetime.utcnow() - timedelta(days=1, hours=17, minutes=30))
        db.session.add_all([comm1_1, comm1_2])

        # Scenario 2: Facilities pipe leakage ticket - In Progress
        c2 = Complaint(
            complaint_number="COM002",
            title="Restroom Water Leakage",
            description="Water pipe leaking in the 2nd-floor restroom. Creating a slip hazard.",
            category_id=created_categories["Washroom"].id,
            department_id=created_departments["Facilities"].id,
            employee_id=sakthivel.id,
            technician_id=lokesh.id,
            priority="High",
            status="In Progress",
            location="2nd Floor Male Restroom",
            created_at=datetime.utcnow() - timedelta(days=1),
            updated_at=datetime.utcnow() - timedelta(hours=6)
        )
        db.session.add(c2)
        db.session.commit()

        # History log for c2
        h2_1 = ComplaintHistory(complaint_id=c2.id, old_status="New", new_status="Assigned", updated_by=naveen.id, updated_at=datetime.utcnow() - timedelta(hours=18))
        h2_2 = ComplaintHistory(complaint_id=c2.id, old_status="Assigned", new_status="Accepted", updated_by=lokesh.id, updated_at=datetime.utcnow() - timedelta(hours=16))
        h2_3 = ComplaintHistory(complaint_id=c2.id, old_status="Accepted", new_status="In Progress", updated_by=lokesh.id, updated_at=datetime.utcnow() - timedelta(hours=15))
        db.session.add_all([h2_1, h2_2, h2_3])

        # Comments for c2
        comm2_1 = Comment(complaint_id=c2.id, user_id=naveen.id, comment="Lokesh, please prioritize this leak immediately.", created_at=datetime.utcnow() - timedelta(hours=17))
        comm2_2 = Comment(complaint_id=c2.id, user_id=lokesh.id, comment="On my way with tools.", created_at=datetime.utcnow() - timedelta(hours=15))
        db.session.add_all([comm2_1, comm2_2])

        # Scenario 3: IT Support Wi-Fi ticket - New (unassigned)
        c3 = Complaint(
            complaint_number="COM003",
            title="Slow Wi-Fi Connection",
            description="Wi-Fi speeds are extremely slow in the conference room. Zoom calls are dropping.",
            category_id=created_categories["Network"].id,
            department_id=created_departments["IT Support"].id,
            employee_id=harish.id,
            priority="Critical",
            status="New",
            location="3rd Floor Conference Room B",
            created_at=datetime.utcnow() - timedelta(hours=2),
            updated_at=datetime.utcnow() - timedelta(hours=2)
        )
        db.session.add(c3)
        db.session.commit()

        print("Database seeding completed successfully!")

# If this file is run directly (python seed.py), run the seed_database function
if __name__ == "__main__":
    seed_database()
