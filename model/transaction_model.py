from datetime import date
from pydantic import BaseModel
from typing import Optional

class Transaction(BaseModel):
    id: str
    ticker: str
    name: str
    quantity: int
    price: float
    transaction_date: date
    
class TransactionCreate(BaseModel):
    ticker: str
    quantity: int
    price: float
    transaction_date: Optional[str] = None

class TransactionUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    transaction_date: Optional[str] = None