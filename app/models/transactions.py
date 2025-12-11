from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    id: int
    date: Optional[datetime]
    client_id: int
    card_id: int
    amount: float
    use_chip: Optional[str]
    merchant_id: Optional[int]
    merchant_city: Optional[str]
    merchant_state: Optional[str]
    zip: Optional[float]
    mcc: Optional[int] = None
    errors: Optional[str] = None

 