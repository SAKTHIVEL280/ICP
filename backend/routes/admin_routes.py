# backend/routes/admin_routes.py
# This route blueprint manages admin-only operations like Departments and Categories CRUD.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.department import Department
from models.category import Category
from models.user import User
from models.complaint import Complaint

admin_bp = Blueprint("admin", __name__)

def check_admin_role():
    claims = get_jwt()
    return claims.get("role") == "Administrator"

# --- Departments CRUD ---

@admin_bp.route("/departments", methods=["GET"])
@jwt_required()
def list_departments():
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
    
    depts = Department.query.order_by(Department.id.asc()).all()
    results = []
    for d in depts:
        users_count = User.query.filter_by(department_id=d.id).count()
        categories_count = Category.query.filter_by(department_id=d.id).count()
        results.append({
            "id": d.id,
            "name": d.name,
            "users_count": users_count,
            "categories_count": categories_count
        })
    return jsonify(results), 200

@admin_bp.route("/departments", methods=["POST"])
@jwt_required()
def create_department():
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    data = request.get_json()
    if not data or not data.get("name") or data.get("name").strip() == "":
        return jsonify({"error": "Department name is required"}), 400
        
    name = data["name"].strip()
    
    existing = Department.query.filter(Department.name.ilike(name)).first()
    if existing:
        return jsonify({"error": "A department with this name already exists"}), 400
        
    dept = Department(name=name)
    db.session.add(dept)
    db.session.commit()
    
    return jsonify({"message": f"Department '{name}' created successfully", "id": dept.id}), 201

@admin_bp.route("/departments/<int:id>", methods=["PUT"])
@jwt_required()
def update_department(id):
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404
        
    data = request.get_json()
    if not data or not data.get("name") or data.get("name").strip() == "":
        return jsonify({"error": "Department name is required"}), 400
        
    name = data["name"].strip()
    
    existing = Department.query.filter(Department.name.ilike(name), Department.id != id).first()
    if existing:
        return jsonify({"error": "A department with this name already exists"}), 400
        
    dept.name = name
    db.session.commit()
    
    return jsonify({"message": "Department updated successfully"}), 200

@admin_bp.route("/departments/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_department(id):
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    dept = Department.query.get(id)
    if not dept:
        return jsonify({"error": "Department not found"}), 404
        
    linked_users = User.query.filter_by(department_id=id).count()
    if linked_users > 0:
        return jsonify({"error": f"Cannot delete department. {linked_users} user(s) are currently assigned to it."}), 400
        
    linked_categories = Category.query.filter_by(department_id=id).count()
    if linked_categories > 0:
        return jsonify({"error": f"Cannot delete department. {linked_categories} category/categories are linked to it."}), 400
        
    db.session.delete(dept)
    db.session.commit()
    return jsonify({"message": "Department deleted successfully"}), 200

# --- Categories CRUD ---

@admin_bp.route("/categories", methods=["GET"])
@jwt_required()
def list_categories():
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    categories = Category.query.order_by(Category.id.asc()).all()
    results = []
    for c in categories:
        complaints_count = Complaint.query.filter_by(category_id=c.id).count()
        results.append({
            "id": c.id,
            "name": c.name,
            "department_id": c.department_id,
            "department_name": c.department.name if c.department else "None",
            "complaints_count": complaints_count
        })
    return jsonify(results), 200

@admin_bp.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    data = request.get_json()
    if not data or not data.get("name") or not data.get("department_id"):
        return jsonify({"error": "Category name and department ID are required"}), 400
        
    name = data["name"].strip()
    dept_id = int(data["department_id"])
    
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({"error": "Selected department does not exist"}), 400
        
    existing = Category.query.filter(Category.name.ilike(name)).first()
    if existing:
        return jsonify({"error": "A category with this name already exists"}), 400
        
    cat = Category(name=name, department_id=dept_id)
    db.session.add(cat)
    db.session.commit()
    return jsonify({"message": f"Category '{name}' created successfully", "id": cat.id}), 201

@admin_bp.route("/categories/<int:id>", methods=["PUT"])
@jwt_required()
def update_category(id):
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    cat = Category.query.get(id)
    if not cat:
        return jsonify({"error": "Category not found"}), 404
        
    data = request.get_json()
    if not data or not data.get("name") or not data.get("department_id"):
        return jsonify({"error": "Category name and department ID are required"}), 400
        
    name = data["name"].strip()
    dept_id = int(data["department_id"])
    
    dept = Department.query.get(dept_id)
    if not dept:
        return jsonify({"error": "Selected department does not exist"}), 400
        
    existing = Category.query.filter(Category.name.ilike(name), Category.id != id).first()
    if existing:
        return jsonify({"error": "A category with this name already exists"}), 400
        
    cat.name = name
    cat.department_id = dept_id
    db.session.commit()
    return jsonify({"message": "Category updated successfully"}), 200

@admin_bp.route("/categories/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_category(id):
    if not check_admin_role():
        return jsonify({"error": "Admin access required"}), 403
        
    cat = Category.query.get(id)
    if not cat:
        return jsonify({"error": "Category not found"}), 404
        
    linked_complaints = Complaint.query.filter_by(category_id=id).count()
    if linked_complaints > 0:
        return jsonify({"error": f"Cannot delete category. {linked_complaints} ticket(s) are raised under this category."}), 400
        
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"message": "Category deleted successfully"}), 200
