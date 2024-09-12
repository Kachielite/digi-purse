from typing import Optional

from pydantic import BaseModel, Field, EmailStr, model_validator

from app.enums.RoleEnum import RoleEnum


class UserRequest(BaseModel):
    username: str = Field(min_length=4)
    email: EmailStr
    phone_number: str
    password: str = Field(min_length=6)
    role: RoleEnum

    class Config:
        json_schema_extra = {
            "example": {
                "username": "Carlos",
                "email": "carlos@email.com",
                "phone_number": "234",
                "password": "strong_password",
                "role": "USER"
            }
        }


class UserUpdateRequest(BaseModel):
    role: Optional[RoleEnum] = None
    is_active: Optional[bool] = None

    @model_validator(mode='before')
    @classmethod
    def check_at_least_one(cls, values):
        if values.get('role') is None and values.get('is_active') is None:
            raise ValueError('At least one of role or is_active must be provided')
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "role": "USER",
                "is_active": True
            }
        }


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: str
    role: RoleEnum
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "Carlos",
                "email": "carlos@mail.com",
                "phone_number": "234",
                "role": "USER",
                "is_active": True,
                "created_at": "2024-08-23T04:57:22.403Z",
                "updated_at": "2024-08-23T04:57:22.403Z"
            }
        }
