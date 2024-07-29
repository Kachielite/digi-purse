from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.utilities.codes import INVALID_TOKEN, AUTHENTICATION_FAILED, TOKEN_EXPIRED

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
EXPIRATION_TIME = settings.access_token_expire_minutes

bcrypt_password = CryptContext(schemes="bcrypt", deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="JWT")


# Encrypt password utility
def encrypt_password(password: str):
    return bcrypt_password.hash(password)


# Dencrypt password utility
def validate_password(password: str, hash_password: str):
    return bcrypt_password.verify(password, hash_password)


# Create token utility
def create_token(username: str, user_id: int, role: str):
    encoded = {"user": username, "id": user_id, "role": role}
    expires_at = datetime.now(timezone.utc) + EXPIRATION_TIME
    encoded.update({"exp": expires_at})
    return jwt.encode(encoded, SECRET_KEY, algorithm=ALGORITHM)


# Get current user
def get_current_user(token: Annotated[str: Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("user")
        user_id = payload.get("id")
        role = payload.get("role")
        expires_at = payload.get("exp")

        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail=TOKEN_EXPIRED)
        if username is None:
            raise HTTPException(status_code=401, detail=AUTHENTICATION_FAILED)
        return {"username": username, "user_id": user_id, "role": role}

    except JWTError:
        raise HTTPException(status_code=401, detail=INVALID_TOKEN)
