from fastapi import APIRouter, HTTPException
from model.watchlist_model import WatchlistItem, WatchlistResponse
from service.watchlist_service import WatchlistService
from typing import List

router = APIRouter()

@router.get("/watchlist", response_model=List[WatchlistResponse])
def get_watchlist():
    try:
        return WatchlistService.fetch_watchlist_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/watchlist")
def add_ticker(item: WatchlistItem):
    try:
        res = WatchlistService.add_ticker_to_watchlist(item.ticker)
        return {"message": "Ticker added", "count": res}
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.delete("/watchlist")
def delete_ticker(item: WatchlistItem):
    try:
        res = WatchlistService.remove_ticker_from_watchlist(item.ticker)
        return {"message": "Ticker removed", "count": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))