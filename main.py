from datetime import date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crud import transaction_create, transaction_update
from database import create_supabase_client
from models import Transaction, TransactionCreate, TransactionUpdate

app = FastAPI()

supabase = create_supabase_client()

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))