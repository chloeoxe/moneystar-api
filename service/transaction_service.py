from datetime import date
from fastapi import HTTPException, status
import pandas as pd
from typing import List, Dict, Any

from repository.transaction_repository import TransactionRepository
from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate

class TransactionService: 
    @staticmethod
    def get_all_transactions() -> List[Transaction]:
        """Fetches all transactions from the repository."""
        return TransactionRepository.get_all_transactions()

    @staticmethod
    def create_transaction(transaction: TransactionCreate) -> Dict[str, Any]:
        try:
            if transaction.quantity == 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Quantity cannot be 0")
            if transaction.price == 0:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Price cannot be 0")
            if transaction.transaction_date is None:
                transaction.transaction_date = date.today()
            return TransactionRepository.create_transaction(transaction)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating transaction: {str(e)}")
    
    @staticmethod
    def update_transaction(transaction_id: str, transaction: TransactionUpdate) -> Dict[str, Any]:
        try:
            if transaction.quantity == 0:
                raise ValueError("Quantity cannot be 0")
            if transaction.price == 0:
                raise ValueError("Price cannot be 0")
            return TransactionRepository.update_transaction(transaction_id, transaction)
        except Exception as e:
            raise Exception(f"Error updating transaction: {str(e)}")
    
    @staticmethod
    def delete_transaction_by_id(transaction_id: str) -> dict[str, Any]:
        try:
            if transaction_id == "":
                raise ValueError("Transaction ID cannot be empty")
            return TransactionRepository.delete_transaction_by_id(transaction_id)
        except Exception as e:
            raise Exception(f"Error deleting transaction: {str(e)}")

    @staticmethod
    def get_transaction_table_data():
        """Fetches transaction data formatted for the transactions table on frontend."""
        transactions = TransactionRepository.get_all_transactions()
        if not transactions:
            return []
        
        transactions =  [t.model_dump() for t in transactions]
        transactions = pd.DataFrame(transactions)
        
        transactions["buy_sell"] = transactions["quantity"].apply(lambda x: "Buy" if x > 0 else "Sell")
        
        return transactions.to_dict(orient='records')