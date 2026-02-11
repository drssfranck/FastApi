from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FraudTransaction(BaseModel):
    """
    Schéma représentant une transaction frauduleuse.
    """

    id: int
    date: Optional[datetime]
    client_id: int
    card_id: int
    amount: float
    use_chip: Optional[str]
    merchant_id: Optional[int]
    merchant_city: Optional[str]
    merchant_state: Optional[str]
    zip: Optional[int]
    mcc: Optional[int]
    errors: Optional[str]
    isFraud: int

    # Configuration Pydantic
    model_config = ConfigDict(from_attributes=True)
