from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List

from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate
from service.transaction_service import TransactionService

router = APIRouter()

@router.get("/transactions", response_model=List[Transaction])
async def get_all_transactions():
    try:
        response = TransactionService.get_all_transactions()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/transaction", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    try:
        response = TransactionService.create_transaction(transaction)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/transaction/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    try:
       response = TransactionService.update_transaction(transaction_id, transaction)
       return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/transaction/{transaction_id}")
async def delete_transaction(transaction_id: str):
    try:
        response = TransactionService.delete_transaction_by_id(transaction_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions-table", response_model=List[Dict[str, Any]])
def get_transaction_table_data():
    """Fetches transaction data formatted for the transactions table on frontend."""
    try:
        response = TransactionService.get_transaction_table_data()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))