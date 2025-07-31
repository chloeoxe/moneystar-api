from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from controller import charts_routes
from crud import portfolio_calc, transactions_read, transaction_create, transaction_update, delete_transaction_by_id, get_historical_prices
from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate
from models import TickersRequest, TickerPrice
from model.position_model import Position

from service.price_service import PriceService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(charts_routes.router)

@app.get("/")
async def root():
    return {"message": "Hello, this is MoneyStar's API!"}

@app.get("/portfolio", response_model=List[Position])
async def read_portfolio():
    try:
        response = await portfolio_calc()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions", response_model=List[Transaction])
async def read_transactions():
    try:
        response = transactions_read()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transaction", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    try:
        res = transaction_create(transaction)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.put("/transaction/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    try:
       res = transaction_update(transaction_id, transaction)
       return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.delete("/transaction/{transaction_id}")
async def delete_transaction(transaction_id: str):
    try:
        response = delete_transaction_by_id(transaction_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
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
