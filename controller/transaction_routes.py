from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List

from exceptions import InsufficientQuantityError, InvalidTransactionError, RepositoryError, TickerNotFoundError
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
        return TransactionService.create_transaction(transaction)
    except TickerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransactionError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except InsufficientQuantityError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.put("/transaction/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction: TransactionUpdate):
    try:
       return TransactionService.update_transaction(transaction_id, transaction)
    except TickerNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InvalidTransactionError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except InsufficientQuantityError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RepositoryError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

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