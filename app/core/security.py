from datetime import datetime, timezone, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
EXPIRATION_TIME = settings.access_token_expire_minutes

bcrypt_password = CryptContext(schemes="bcrypt", deprecated="auto")


# Encrypt password
def encrypt_password(password: str):
    return bcrypt_password.hash(password)


# Dencrypt password
def validate_password(password: str, hash_password: str):
    return bcrypt_password.verify(password, hash_password)


# Create token
def create_token(username: str, user_id: int, role: str):
    encoded = {"user": username, "id": user_id, "role": role}
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_TIME)
    encoded.update({"exp": expires_at})
    return jwt.encode(encoded, SECRET_KEY, algorithm=ALGORITHM)


# Decode token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("user")
        user_id = payload.get("id")
        role = payload.get("role")
        expires_at = payload.get("exp")
        return {"username": username, "user_id": user_id, "role": role, "expires_at": expires_at}
    except (JWTError, ValidationError) as e:
        raise ValueError("Invalid token") from e
