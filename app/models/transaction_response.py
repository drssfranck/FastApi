from pydantic import BaseModel
from typing import List
from app.models.transactions import Transaction


class TransactionListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    data: List[Transaction]
