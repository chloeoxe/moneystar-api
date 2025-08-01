from typing import List, Dict, Any

from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate
from repository.database import create_supabase_client

class TransactionRepository:
    
    @staticmethod
    def get_all_transactions() -> List[Transaction]:
        client = create_supabase_client()
        response = client.table("transactions").select("*").execute()
        if not response.data:
            return []
        return [Transaction(**t) for t in response.data]
    
    @staticmethod
    def create_transaction(transaction: TransactionCreate) -> Dict[str, Any]:
        client = create_supabase_client()
        response = client.table("transactions").insert({
            "ticker": transaction.ticker,
            "name": transaction.name,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "transaction_date": str(transaction.transaction_date)
        }).execute()
        if not response.data:
            raise ValueError("Failed to create transaction: no data returned")
        return response.data[0]
    
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
