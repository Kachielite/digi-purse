from pydantic import BaseModel, Field, EmailStr

from app.enums.RoleEnum import RoleEnum


class UserRequest(BaseModel):
    username: str = Field(min_length=4)
    email: EmailStr
    phone_number: str
    password: str = Field(min_length=6)
    role: RoleEnum


    class Config:
        schema_extra = {
            "example": {
                "username": "Carlos",
                "email": "carlos@email.com",
                "phone_number": "234",
                "password": "strong_password",
                "role": "USER"
            }
        }
