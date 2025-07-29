from datetime import date
from typing import Optional
from pydantic import BaseModel

class Transaction(BaseModel):
    id: str
    ticker: str
    name: str
    quantity: int
    price: float
    transaction_date: date

class TransactionCreate(BaseModel):
    ticker: str
    name: str
    quantity: int
    price: float
    transaction_date: Optional[date] = None