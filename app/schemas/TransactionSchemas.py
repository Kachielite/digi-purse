from pydantic import BaseModel


class TransactionRequest(BaseModel):
    amount: float
    source: str
    destination: str
    type: str

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.0,
                "source": "wallet",
                "type": "credit",
                "destination": "238492QWE"
            }
        }


class TransactionResponse(BaseModel):
    id: str
    wallet_id: str
    amount: float
    type: str
    description: str
    source: str
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "238492QWE",
                "wallet_id": "238492QWE",
                "amount": 100.0,
                "type": "credit",
                "description": "Top up wallet by System Admin: admin",
                "source": "wallet",
                "created_at": "2021-09-01T12:00:00Z",
                "updated_at": "2021-09-01T12:00:00Z"
            }
        }
