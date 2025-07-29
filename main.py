from datetime import date
from fastapi import FastAPI, HTTPException
from crud import insert_transaction, delete_transaction_by_id
from database import create_supabase_client
from models import Transaction, TransactionCreate

app = FastAPI()

supabase = create_supabase_client()

@app.get("/")
async def root():
    return {"message": "Hello, this is MoneyStar's API!"}

@app.get("/transactions")
async def get_transactions():
    response = (
        supabase.table("transactions")
        .select("*", count="exact")
        .execute()
    )
    return response

@app.post("/transaction", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    try:
        res = insert_transaction(transaction)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/transaction/{transaction_id}")
async def delete_transaction(transaction_id: str):
    try:
        response = delete_transaction_by_id(transaction_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))