from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from controller import chart_routes, transaction_routes, portfolio_routes
from crud import get_historical_prices
from models import TickersRequest, TickerPrice


from service.price_service import PriceService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chart_routes.router)
app.include_router(transaction_routes.router)
app.include_router(portfolio_routes.router)

@app.get("/")
async def root():
    return {"message": "Hello, this is MoneyStar's API!"}

@app.get("/prices")
async def get_prices():
    try:
        response = get_historical_prices()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/prices/live", response_model=List[TickerPrice])
async def get_live_prices_for_tickers(request: TickersRequest):
    try:
        data = await PriceService.fetch_live_prices(request.tickers)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
