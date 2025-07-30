from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crud import transactions_read, transaction_create, transaction_update, delete_transaction_by_id, get_portfolio_linechart_data, get_historical_prices, get_portfolio_distribution_data, get_top_holdings_performance_data
from models import Transaction, TransactionCreate, TransactionUpdate
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello, this is MoneyStar's API!"}

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
    
@app.get("/portfolio/linechart")
async def get_portfolio_linechart():
    try:
        data = get_portfolio_linechart_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/prices")
async def get_prices():
    try:
        response = get_historical_prices()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/portfolio/distribution")
async def get_portfolio_distribution():
    try:
        response = get_portfolio_distribution_data()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/portfolio/topholdingsperformance")
async def get_portfolio_barchart():
    try:
        response = get_top_holdings_performance_data()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))