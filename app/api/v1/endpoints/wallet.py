from typing import List

from fastapi import APIRouter, HTTPException, Query, Path
from starlette import status

from app.core.dependency import user_dependency, db_dependency
from app.crud.crud_wallet import read_all_wallet, read_wallet_details, create_wallet, block_user_wallet, \
    delete_user_wallet
from app.schemas.MessageResponseSchema import MessageResponse
from app.schemas.WalletSchemas import WalletCreationRequest, WalletUpdateRequest, WalletInfoResponse
from app.utilities.extract_user_info import get_user_info

router = APIRouter(tags=["Manage Wallets"], prefix="/wallets")


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[WalletInfoResponse])
async def read_all_wallets(user: user_dependency, db: db_dependency, limit: int = Query(10, gt=0),
                           offset: int = Query(0, ge=0)):
    code, response = read_all_wallet(db, get_user_info(user), limit, offset)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.get("/details", status_code=status.HTTP_200_OK, response_model=WalletInfoResponse)
async def read_wallet(user: user_dependency, db: db_dependency, phone_number: str = Query(None),
                      user_id: int = Query(None), wallet_id: str = Query(None)):
    code, response = read_wallet_details(db, get_user_info(user), user_id, wallet_id, phone_number)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def wallet_creation(user: user_dependency, db: db_dependency, wallet: WalletCreationRequest):
    code, response = create_wallet(db, get_user_info(user), wallet)

    if code != 201:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response


@router.put("/{wallet_id}", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def block_wallet(user: user_dependency, db: db_dependency, wallet_update: WalletUpdateRequest,
                       wallet_id: str = Path(min_length=8)):
    code, response = block_user_wallet(get_user_info(user), db, wallet_id, wallet_update)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))

    return response


@router.delete("/{wallet_id}", status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def delete_wallet(user: user_dependency, db: db_dependency, wallet_id: str = Path()):
    code, response = delete_user_wallet(db, get_user_info(user), wallet_id)

    if code != 200:
        raise HTTPException(status_code=code, detail=response.get("message"))
    return response
