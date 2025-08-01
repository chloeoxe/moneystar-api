from fastapi import APIRouter, HTTPException
from typing import List

from model.position_model import Position, PositionSummary
from service.portfolio_service import PortfolioService

router = APIRouter()

@router.get("/summary", response_model=PositionSummary)
async def get_portfolio_summary():
    try:
        response = await PortfolioService.portfolio_summary()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio", response_model=List[Position])
async def get_portfolio():
    try:
        response = await PortfolioService.portfolio_calc()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))