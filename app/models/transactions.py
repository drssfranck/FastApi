from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class Transaction(BaseModel):
    id: int
    date: Optional[str]
    client_id: int
    card_id: int
    amount: float
    use_chip: Optional[str]
    merchant_id: Optional[int]
    merchant_city: Optional[str]
    merchant_state: Optional[str]
    zip: Optional[float]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 7475327,
                "date": "2010-01-01T00:01:00",
                "client_id": 1556,
                "card_id": 2972,
                "amount": -77.00,
                "use_chip": "Swipe Transaction",
                "merchant_id": 59935,
                "merchant_city": "Beulah",
                "merchant_state": "ND",
                "zip": 58523.0
            }
        }
