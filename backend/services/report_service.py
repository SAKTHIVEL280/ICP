# backend/services/report_service.py
# This service handles database aggregation queries to generate stats and analytics for dashboard reports.
# It uses SQLAlchemy functions like count and group_by to aggregate data.

# Import db instance to execute queries
from extensions import db
# Import models to run join and group queries on
from models.complaint import Complaint
from models.department import Department
from models.category import Category

# Import SQLAlchemy func to use database functions like extract or to_char
from sqlalchemy import func

def get_complaint_summary():
    """
    Generates a basic count summary of complaints based on their status:
    - Total: all tickets
    - Open: New, Assigned, Accepted, In Progress, Resolved, Employee Verification
    - Resolved: Resolved
    - Closed: Closed
    - Rejected: Rejected
    
    Returns:
    - dict: A dictionary with status counts.
    """
    # Run queries to count instances in various states
    total_count = Complaint.query.count()
    closed_count = Complaint.query.filter_by(status="Closed").count()
    resolved_count = Complaint.query.filter_by(status="Resolved").count()
    rejected_count = Complaint.query.filter_by(status="Rejected").count()
    
    # Open is defined as anything that is not closed or rejected
    open_count = total_count - closed_count - rejected_count
    
    return {
        "total": total_count,
        "open": open_count,
        "resolved": resolved_count,
        "closed": closed_count,
        "rejected": rejected_count
    }

def get_complaints_by_department():
    """
    Aggregates complaints by department and returns the counts and department names.
    Useful for bar charts.
    
    Returns:
    - List[dict]: A list of objects with "department_name" and "count"
    """
    # Perform a group_by query joining Complaint and Department
    results = db.session.query(
        Department.name, 
        func.count(Complaint.id)
    ).join(
        Complaint, 
        Department.id == Complaint.department_id
    ).group_by(
        Department.name
    ).all()
    
    # Map results to a clean list of dictionaries
    return [{"department": r[0], "count": r[1]} for r in results]

def get_complaints_by_category():
    """
    Aggregates complaints by category and returns the counts and category names.
    
    Returns:
    - List[dict]: A list of objects with "category_name" and "count"
    """
    results = db.session.query(
        Category.name, 
        func.count(Complaint.id)
    ).join(
        Complaint, 
        Category.id == Complaint.category_id
    ).group_by(
        Category.name
    ).all()
    
    return [{"category": r[0], "count": r[1]} for r in results]

def get_complaints_by_priority():
    """
    Aggregates complaints by priority.
    
    Returns:
    - List[dict]: A list of objects with "priority" and "count"
    """
    results = db.session.query(
        Complaint.priority, 
        func.count(Complaint.id)
    ).group_by(
        Complaint.priority
    ).all()
    
    return [{"priority": r[0], "count": r[1]} for r in results]

def get_monthly_complaints():
    """
    Aggregates complaints by month of creation. Uses PostgreSQL's TO_CHAR function
    to format the created_at timestamp into 'YYYY-MM' strings.
    
    Returns:
    - List[dict]: A list of objects with "month" (e.g. "2026-07") and "count"
    """
    # group by the formatted month string
    results = db.session.query(
        func.to_char(Complaint.created_at, "YYYY-MM").label("month"),
        func.count(Complaint.id)
    ).group_by(
        "month"
    ).order_by(
        "month"
    ).all()
    
    return [{"month": r[0], "count": r[1]} for r in results]
