from fastapi import APIRouter, HTTPException, Path
from starlette import status

from app.core.dependency import user_dependency, db_dependency
from app.crud.crud_user import create_user, delete_user, update_user_data, get_all_users
from app.schemas.UserSchemas import UserRequest, UserUpdateRequest
from app.utilities.extract_user_info import get_user_info

router = APIRouter(tags=["Manage Users"], prefix="/users")


@router.get("/", status_code=status.HTTP_200_OK)
async def list_all_users(user: user_dependency, db: db_dependency):
    code, response = get_all_users(db, get_user_info(user))
    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_user(user: user_dependency, db: db_dependency, user_data: UserRequest):
    code, response = create_user(user_data, db, get_user_info(user))
    if code != 201:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user: user_dependency, db: db_dependency, update: UserUpdateRequest,
                      user_id: int = Path(gt=0)):
    code, response = update_user_data(update, user_id, get_user_info(user), db)
    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    code, response = delete_user(get_user_info(user), db, user_id)
    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response
