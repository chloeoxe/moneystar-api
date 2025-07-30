from datetime import date
from typing import Optional
from pydantic import BaseModel

class Position(BaseModel):
    ticker: str
    name: str
    quantity: int
    avg_price: float
    live_price: float
    price_delta: float
    pct_delta: float
    pnl: float

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
    transaction_date: Optional[str] = None

class TransactionUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    transaction_date: Optional[str] = None