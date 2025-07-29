from datetime import date
from typing import Any
from models import TransactionCreate, TransactionUpdate
from database import client

def transactions_read() -> list[dict[str, Any]]:
    response = client.table("transactions").select("*", count="exact").execute()
    return response.data

def transaction_create(transaction: TransactionCreate) -> dict[str, Any]:
    try:
        if transaction.quantity == 0:
            raise ValueError("Quantity cannot be 0")
        if transaction.price == 0:
            raise ValueError("Price cannot be 0")
        if transaction.transaction_date is None:
            transaction.transaction_date = date.today()

        res = client.table("transactions").insert({
            "ticker": transaction.ticker,
            "name": transaction.name,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "transaction_date": str(transaction.transaction_date)
        }).execute()

        if not res.data:
            raise ValueError("Failed to create transaction: no data returned")
        return res.data[0]
    except Exception as e:
        raise Exception(f"Error creating transaction: {str(e)}")

def transaction_update(transaction_id: str, transaction: TransactionUpdate) -> dict[str, Any]:
    try:
        if transaction.quantity == 0:
            raise ValueError("Quantity cannot be 0")
        if transaction.price == 0:
            raise ValueError("Price cannot be 0")

        data = {k: v for k, v in transaction.model_dump().items() if v is not None}

        res = client.table("transactions").update(data).eq("id", transaction_id).execute()

        if not res.data:
            raise ValueError("Failed to update transaction: no data returned")
        return res.data[0]

    except Exception as e:
        raise Exception(f"Error updating transaction: {str(e)}")
    
def delete_transaction_by_id(transaction_id: str) -> dict[str, Any]:
    try:
        response = client.table("transactions").delete().eq("id", transaction_id).execute()
        if len(response.data) == 0:
            raise ValueError(f"Transaction with id={transaction_id} not found")
        
        return {"message": f"Transaction with id={transaction_id} deleted successfully"}
    except Exception as e:
        raise Exception(f"Error deleting transaction: {str(e)}")
