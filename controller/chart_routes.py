from fastapi import APIRouter, HTTPException

from service.chart_service import ChartService

router = APIRouter()

@router.get("/charts/portfolio-linechart")
async def get_portfolio_linechart():
    try:
        data = ChartService.get_portfolio_linechart_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/charts/portfolio-piechart")
async def get_portfolio_piechart():
    try:
        data = await ChartService.get_portfolio_distribution_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/portfolio-barchart")
async def get_portfolio_barchart():
    try:
        data = await ChartService.get_top_holdings_performance_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))