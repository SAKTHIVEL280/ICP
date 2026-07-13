from models.user import User
from extensions import db
import bcrypt
from flask_jwt_extended import create_access_token

def register_user(data):

    if User.query.filter_by(email=data["email"]).first():
        return None, "Email already exists"

    if User.query.filter_by(employee_id=data["employee_id"]).first():
        return None, "Employee ID already exists"

    hashed_password = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        employee_id=data["employee_id"],
        name=data["name"],
        email=data["email"],
        password=hashed_password,
        role=data["role"],
        department_id=data["department_id"]
    )

    db.session.add(user)
    db.session.commit()

    return user, None
def login_user(data):

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return None, "Invalid email or password"

    if not bcrypt.checkpw(
        data["password"].encode(),
        user.password.encode()
    ):
        return None, "Invalid email or password"

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role,
            "name": user.name
        }
    )

    return token, None