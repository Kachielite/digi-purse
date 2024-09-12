from pydantic import BaseModel


class LoyaltyRedeemSchema(BaseModel):
    user_id: int
    quantity: int

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "quantity": 10
            }
        }


class LoyaltyInfoResponseSchema(BaseModel):
    id: int
    user_id: int
    points: int
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "points": 0,
                "created_at": "2024-08-23T04:57:22.403Z",
                "updated_at": "2024-08-23T04:57:22.403Z"
            }
        }
