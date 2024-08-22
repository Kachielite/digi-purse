from sqlalchemy.orm import Session

from app.core.security import encrypt_password
from app.models.User import User
from app.schemas.UserSchemas import UserRequest, UserUpdateRequest, UserResponse


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def check_admin_user(user: dict):
    _, user_info = user
    if user_info is None or user_info.get("role") in ["ADMIN", "SYS_ADMIN"]:
        return user_info
    else:
        return None


# Get all users
def get_all_users(db: Session, user: dict):
    if check_admin_user(user) is None:
        return 401, {"message": "You do not have enough permission to view users"}
    users = db.query(User).all()
    return 200, [UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(timespec='milliseconds') + 'Z'
    ) for user in users]


# Create new user
def create_user(user_to_be_created: UserRequest, db: Session, user: dict):
    if check_admin_user(user) is None:
        return 401, {"message": "You do not have enough permission to create users"}
    if db.query(User).filter(User.email == user_to_be_created.email).first():
        return 403, {"message": "User with the associated email already exist"}
    if db.query(User).filter(User.phone_number == user_to_be_created.phone_number).first():
        return 403, {"message": "User with the associated phone number already exist"}
    if db.query(User).filter(User.username == user_to_be_created.username).first():
        return 403, {"message": "User with the associated username already exist"}
    new_user = User(
        username=user_to_be_created.username,
        email=user_to_be_created.email,
        phone_number=user_to_be_created.phone_number,
        hash_password=encrypt_password(user_to_be_created.password),
        role=user_to_be_created.role,
        is_active=True
    )
    print(new_user)

    db.add(new_user)
    db.commit()
    return 201, {"message": "User created successfully"}


# Update user data
def update_user_data(user_to_be_updated: UserUpdateRequest,
                     user_id: int, user: dict, db: Session):
    if check_admin_user(user) is None:
        return 401, {"message": "You do not have enough permission to update users"}

    user_data = get_user(db, user_id)
    if user_data is None:
        return 404, {"message": "User not found"}

    if user_to_be_updated.role:
        user_data.role = user_to_be_updated.role
    if user_to_be_updated.is_active:
        user_data.is_active = user_to_be_updated.is_active

    db.add(user_data)
    db.commit()
    return 200, {"message": "User role updated successfully"}


# Delete user
def delete_user(user: dict, db: Session, user_id: int):
    _, user_info = user
    user_to_be_deleted = get_user(db, user_id)
    if user_to_be_deleted is None:
        return 404, {"message": "User not found"}
    if user_info.get("role") == "USER":
        return 401, {"message": "You do not have enough permission to delete users"}
    if user_info.get("role") != "SYS_ADMIN" and user_to_be_deleted.role == "ADMIN":
        return 401, {"message": "Only Sys admin can delete Admin users"}
    if user_info.get("role") == "ADMIN" and user_to_be_deleted.role == "SYS_ADMIN":
        return 401, {"message": "Only Sys admin can delete a Sys admin user"}
    if user_info.get("role") in ["SYS_ADMIN", "ADMIN"] and user_to_be_deleted.role == "USER":
        db.query(User).filter(User.id == user_to_be_deleted.id).delete()
        db.commit()
    return 200, {"message": "User deleted successfully"}
