from datetime import date
from typing import List, Dict, Any

from fastapi import HTTPException, status

from exceptions import InsufficientQuantityError, RepositoryError
from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate
from repository.database import create_supabase_client

class TransactionRepository:
    
    @staticmethod
    def get_all_transactions() -> List[Transaction]:
        client = create_supabase_client()
        response = client.table("transactions").select("*").order("transaction_date", desc=True).execute()
        if not response.data:
            return []
        return [Transaction(**t) for t in response.data]

    @staticmethod
    def get_ticker_qty(ticker: str) -> int:
        client = create_supabase_client()
        curr_qty = client.table("transactions").select("quantity").eq("ticker", ticker).execute()
        return sum(item['quantity'] for item in curr_qty.data) if curr_qty.data else 0

    @staticmethod
    def get_transaction_by_id(transaction_id: str) -> Transaction:
        client = create_supabase_client()
        response = client.table("transactions").select("*").eq("id", transaction_id).execute()
        if not response.data:
            raise ValueError(f"Transaction with id={transaction_id} not found")
        return Transaction(**response.data[0])
    
    @staticmethod
    def create_transaction(transaction: TransactionCreate, name: str) -> Dict[str, Any]:
        try:
            client = create_supabase_client()
            response = client.table("transactions").insert({
                "ticker": transaction.ticker,
                "name": name,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "transaction_date": str(transaction.transaction_date)
            }).execute()
            if not response.data:
                raise RepositoryError("No data returned from transaction creation")
            return response.data[0]
        except Exception as e:
            raise RepositoryError(f"Supabase error: {str(e)}")
    
    @staticmethod
    def update_transaction(transaction_id: str, transaction: TransactionUpdate) -> Dict[str, Any]:
        data = {k: v for k, v in transaction.model_dump().items() if v is not None}
        
        client = create_supabase_client()
        res = client.table("transactions").update(data).eq("id", transaction_id).execute()
        if not res.data:
            raise ValueError("Failed to update transaction: no data returned")
        return res.data[0]
    
    @staticmethod
    def delete_transaction_by_id(transaction_id: str) -> Dict[str, Any]:
        client = create_supabase_client()
        response = client.table("transactions").delete().eq("id", transaction_id).execute()
        if len(response.data) == 0:
            raise ValueError(f"Transaction with id={transaction_id} not found")
        return {"message": f"Transaction with id={transaction_id} deleted successfully"}

    @staticmethod
    def get_buy_transactions() -> List[Dict[str, Any]]:
        client = create_supabase_client()
        response = client.table("transactions") \
            .select("ticker,transaction_date") \
            .gt("quantity", 0) \
            .execute()

        if not response.data:
            return []

        return response.data