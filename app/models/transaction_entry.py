from pydantic import BaseModel
class TransactionEntry(BaseModel):
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float