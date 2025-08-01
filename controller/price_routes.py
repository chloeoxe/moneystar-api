from fastapi import APIRouter, HTTPException
from typing import List

from service.price_service import PriceService
from model.price_model import TickersLivePriceRequest, TickerPrice

router = APIRouter()

@router.get("/prices", response_model=List[TickerPrice])
async def get_historical_prices():
    try:
        response = PriceService.get_historical_prices()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/prices/live", response_model=List[TickerPrice])
async def get_live_prices_for_tickers(request: TickersLivePriceRequest):
    try:
        data = await PriceService.fetch_live_prices(request)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))