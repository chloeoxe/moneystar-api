from pydantic import BaseModel

class WatchlistItem(BaseModel):
    ticker: str

class WatchlistResponse(BaseModel):
    ticker: str
    price: float
    change_pct: float
    high: float
    low: float
    volume: int