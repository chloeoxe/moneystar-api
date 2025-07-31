from datetime import date
from typing import List, Dict, Optional
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
    transaction_date: Optional[str] = None

class TransactionUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    transaction_date: Optional[str] = None

class TickersRequest(BaseModel):
    tickers: List[str]

class TickerPrice(BaseModel):
    ticker: str
    price: Optional[float]  # None if invalid/cannot be found