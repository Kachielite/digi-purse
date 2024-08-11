from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import encrypt_password, oauth2_bearer, validate_password, create_token
from app.db.session import get_db
from app.models.User import User
from app.schemas import UserRequest

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
EXPIRATION_TIME = settings.access_token_expire_minutes

db_dependency = Annotated[Session, Depends(get_db)]


# Create new user
def create_new_user(db: db_dependency, user: UserRequest):
    new_user = User(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        hash_password=encrypt_password(user.password),
        is_active=True
    )

    db.add(new_user)
    db.commit()


# Get current user
def get_current_user(token: Annotated[str: Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("user")
        user_id = payload.get("id")
        role = payload.get("role")
        expires_at = payload.get("exp")

        if expires_at < datetime.now(timezone.utc):
            return {"code": 401, "message": "token expired"}
        if username is None:
            return {"code": 401, "message": "Invalid token"}
        return {"username": username, "user_id": user_id, "role": role}
    except JWTError:
        return {"code": 401, "message": "Authentication failed"}


# Authenticate user
def authenticate_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None:
        return {"code": 404, "message": "User not found"}
    if not validate_password(form_data.password, user.hash_password):
        return {"code": 401, "message": "Wrong Credentials"}
    token = create_token(user.username, user.id, user.role)
    return {"access_token": token, "token_type": "bearer"}

