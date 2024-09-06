from typing import List

from fastapi import APIRouter, HTTPException
from starlette import status

from app.core.dependency import db_dependency, user_dependency
from app.crud.crud_transaction import top_wallet, transaction_all_history, transaction_by_id, transaction_user_history, \
    debit_wallet
from app.schemas.MessageResponseSchema import MessageResponse
from app.schemas.TransactionSchemas import TransactionRequest, TransactionResponse
from app.utilities.extract_user_info import get_user_info

router = APIRouter(prefix="/transactions", tags=["Manage Transactions"])


@router.post("/top-wallet", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def top_up_user_wallet(db: db_dependency, user: user_dependency, request: TransactionRequest):
    code, response = top_wallet(db, get_user_info(user), request)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.post("/debit-wallet", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def debit_user_wallet(db: db_dependency, user: user_dependency, request: TransactionRequest):
    code, response = debit_wallet(db, get_user_info(user), request)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TransactionResponse])
async def read_all_transactions(user: user_dependency, db: db_dependency, limit: int = 10, offset: int = 0):
    code, response = transaction_all_history(db, get_user_info(user), limit, offset)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.get("/{transaction_id}", status_code=status.HTTP_200_OK, response_model=TransactionResponse)
async def read_transaction_by_id(transaction_id: str, db: db_dependency, user: user_dependency):
    code, response = transaction_by_id(db, get_user_info(user), transaction_id)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[TransactionResponse])
async def read_user_transactions(user_id: str, db: db_dependency, user: user_dependency, limit: int = 10, offset: int = 0):
    code, response = transaction_user_history(db, get_user_info(user), user_id, limit, offset)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response
