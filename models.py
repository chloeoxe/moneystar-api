from datetime import date
from typing import List, Optional
from pydantic import BaseModel

class TickersRequest(BaseModel):
    tickers: List[str]
    target_date: Optional[str] = None
    interval: Optional[str] = "5m"

class TickerPrice(BaseModel):
    ticker: str
    date: Optional[date]
    price: Optional[float]  # None if invalid/cannot be found