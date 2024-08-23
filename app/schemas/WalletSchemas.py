from pydantic import BaseModel
from sqlalchemy import true, false


class WalletCreationRequest(BaseModel):
    user_id: int
    user_phone_number: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "user_phone_number": "234"
            }
        }


class WalletInfoResponse(BaseModel):
    id: str
    user_id: int
    user_phone_number: str
    balance: int
    is_blocked: bool
    is_deleted: bool
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "string",
                "user_id": 1,
                "user_phone_number": "string",
                "is_blocked": True,
                "is_deleted": False,
                "balance": 0,
                "created_at": "2024-08-23T04:57:22.403Z",
                "updated_at": "2024-08-23T04:57:22.403Z"
            }
        }


class WalletUpdateRequest(BaseModel):
    is_blocked: bool

    class Config:
        json_schema_extra = {
            "example": {
                "is_blocked": True,
            }
        }
