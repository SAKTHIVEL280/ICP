from extensions import db
from models.user import User
import bcrypt


def register_user(data):
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

    return user