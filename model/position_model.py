from pydantic import BaseModel

class PositionSummary(BaseModel):
    total_value: float
    total_value_pct: float
    monthly_pnl: float
    monthly_pnl_pct: float
    all_time_returns: float
    all_time_returns_pct: float
    cash: float
    cash_pct: float

class Position(BaseModel):
    id: str
    ticker: str
    name: str
    quantity: int
    avg_price: float
    live_price: float
    price_delta: float
    pct_delta: float
    pnl: float
