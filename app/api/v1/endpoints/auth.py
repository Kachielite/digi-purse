from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.core.dependency import db_dependency
from app.crud.crud_auth import create_new_user, authenticate_user, get_current_user, oauth2_bearer
from app.schemas.UserSchemas import UserRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


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
