from typing import List, Optional
from pydantic import BaseModel

class TickersRequest(BaseModel):
    tickers: List[str]

class TickerPrice(BaseModel):
    ticker: str
    price: Optional[float]  