from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    username: str
    user_id: int
    role: str

    class Config:
        json_schema_extra = {
            "example":{
                "username": "username",
                "user_id": "2",
                "role": "USER"
            }
        }


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJxxxxxxxxxxxxxxxxxxxxxx",
                "token_type": "bearer"
            }
        }
