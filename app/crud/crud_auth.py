from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import encrypt_password, validate_password, create_token, decode_token
from app.db.session import get_db
from app.models.User import User
from app.schemas.UserSchemas import UserRequest

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
EXPIRATION_TIME = settings.access_token_expire_minutes

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="JWT")


# Create new user
def create_new_user(user_to_be_created: UserRequest, db: Session):
    new_user = User(
        username=user_to_be_created.username,
        email=user_to_be_created.email,
        phone_number=user_to_be_created.phone_number,
        hash_password=encrypt_password(user_to_be_created.password),
        role=user_to_be_created.role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    return 201, {"message": "User created successfully"}


# Get current user
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: Annotated[Session, Depends(get_db)]):
    try:
        token_data = decode_token(token)
        if token_data.get("expires_at") < datetime.now(timezone.utc).timestamp():
            return 401, {"message": "token expired"}
        username = db.query(User).filter(User.username == token_data.get('username')).first()
        if username is None:
            return 401, {"message": "Invalid token"}
        return 200, {"username": token_data.get("username"), "user_id": token_data.get("user_id"), "role": token_data.get("role")}
    except ValueError:
        return 401, {"message": "Authentication failed"}


# Authenticate user
def authenticate_user(form_data: OAuth2PasswordRequestForm, db: Session):
    user = db.query(User).filter(User.email == form_data.username).first()
    if user is None:
        return 404, {"message": "User not found"}

    if not validate_password(form_data.password, user.hash_password):
        return 401, {"message": "Wrong Credentials"}

    token = create_token(user.username, user.id, user.role)
    return 200, {"access_token": token, "token_type": "bearer"}
