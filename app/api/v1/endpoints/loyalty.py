from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.core.dependency import db_dependency, user_dependency
from app.crud.crud_loyalty import read_all_loyalties, redeem_loyalty_points, read_user_loyalty
from app.schemas.LoyaltySchemas import LoyaltyInfoResponseSchema, LoyaltyRedeemSchema
from app.schemas.MessageResponseSchema import MessageResponse
from app.utilities.extract_user_info import get_user_info

router = APIRouter(prefix="/loyalty", tags=["Manage Loyalties"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[LoyaltyInfoResponseSchema])
async def read_loyalties(db: db_dependency, user: user_dependency, limit: int = 10, offset: int = 0):
    code, response = read_all_loyalties(db, get_user_info(user), limit, offset)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=LoyaltyInfoResponseSchema)
async def read_loyalty(user_id: int, db: db_dependency, user: user_dependency):
    code, response = read_user_loyalty(db, get_user_info(user), user_id)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.post("/redeem", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def redeem_points(db: db_dependency, user: user_dependency, request: LoyaltyRedeemSchema):
    code, response = redeem_loyalty_points(db, get_user_info(user), request)

    if code != 201:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response
