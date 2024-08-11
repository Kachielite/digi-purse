from pydantic import BaseModel, Field, EmailStr


class UserRequest(BaseModel):
    id: int = Field(description="ID not required on creation", default=None)
    username: str = Field(min_length=4)
    email: EmailStr
    phone_number: str
    password: Field(min_length=6)
    role: str

    model_config = {
        'json_schema_extra': {
            'username': 'Carlos',
            'email': 'carlos@email.com',
            'phone_number' : '234XXXXXXXXXXX',
            'password': 'xxxxxxxxxxx',
            'role': 'USER'
        }
    }