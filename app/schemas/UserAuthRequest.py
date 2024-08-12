from pydantic import BaseModel, Field, EmailStr


class UserAuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

    model_config = {
        'json_schema_extra': {
            'email': 'carlos@email.com',
            'password': 'xxxxxxxxxxx',
        }
    }