from datetime import date
from typing import List, Optional, Dict
from pydantic import BaseModel

class TickersLivePriceRequest(BaseModel):
    tickers: List[str]
    target_date: Optional[str] = None
    interval: Optional[str] = "5m"

class TickerPrice(BaseModel):
    ticker: str
    date: Optional[date]
    close: Optional[float]  # None if invalid/cannot be found

class PriceUpdateRequest(BaseModel):
    years_to_keep: Optional[int] = 5
    months_before_earliest: Optional[int] = 2

class PriceUpdateResponse(BaseModel):
    tickers_updated: List[str]
    total_new_prices_added: int
    total_old_prices_deleted: int
    update_details: Dict[str, int]

class TickerPriceUpdateRequest(BaseModel):
    ticker: str
    earliest_buy_date: date
    years_to_keep: Optional[int] = 5
    months_before_earliest: Optional[int] = 2
    
class TickerPriceUpdateResponse(BaseModel):
    ticker: str
    missing_dates_fetched: int