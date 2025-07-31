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
