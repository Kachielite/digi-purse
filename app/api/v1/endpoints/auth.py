from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from app.db.session import get_db
from app.schemas.UserRequest import UserRequest
from app.crud.crud_auth import create_new_user, authenticate_user, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token", scheme_name="JWT")


# Create new user
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def new_user(db: db_dependency, user: UserRequest):
    code, response = create_new_user(user, db)
    if code != 201:
        raise HTTPException(status_code=code, detail=response["message"])
    return response


# Authenticate user
@router.post("/token", status_code=status.HTTP_200_OK)
async def authenticate(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    code, response = authenticate_user(form_data, db)
    if code != 200:
        raise HTTPException(status_code=code, detail=response["message"])
    return response


@router.get("/me", status_code=status.HTTP_200_OK)
async def current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    code, response = get_current_user(token, db)
    if code != 200:
        raise HTTPException(status_code=code, detail=response["message"])
    return response
