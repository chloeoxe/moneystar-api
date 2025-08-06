import yfinance as yf
from datetime import date
from fastapi import HTTPException, status
import pandas as pd
from typing import List, Dict, Any

from exceptions import InsufficientQuantityError, InvalidTransactionError, TickerNotFoundError
from repository.transaction_repository import TransactionRepository
from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate

class TransactionService: 
    @staticmethod
    def get_all_transactions() -> List[Transaction]:
        """Fetches all transactions from the repository."""
        return TransactionRepository.get_all_transactions()

    @staticmethod
    def create_transaction(transaction: TransactionCreate) -> Dict[str, Any]:
        stock = yf.Ticker(transaction.ticker)
        name = stock.info.get("longName") or stock.info.get("shortName")
        qty = TransactionRepository.get_ticker_qty(transaction.ticker)
        if not name:
            raise TickerNotFoundError("Ticker does not exist")
        if transaction.quantity == 0:
            raise InvalidTransactionError("Quantity cannot be 0")
        if transaction.price == 0:
            raise InvalidTransactionError("Price cannot be 0")
        if qty + transaction.quantity < 0:
            raise InsufficientQuantityError("Insufficient quantity for this transaction")
        if transaction.transaction_date is None:
            transaction.transaction_date = date.today()
        return TransactionRepository.create_transaction(transaction, name)
    
    @staticmethod
    def update_transaction(transaction_id: str, transaction: TransactionUpdate) -> Dict[str, Any]:
        stock = yf.Ticker(transaction.ticker)
        name = stock.info.get("longName") or stock.info.get("shortName")
        qty = TransactionRepository.get_ticker_qty(transaction.ticker)
        if not name:
            raise TickerNotFoundError("Ticker does not exist")
        if transaction.quantity == 0:
            raise InvalidTransactionError("Quantity cannot be 0")
        if transaction.price == 0:
            raise InvalidTransactionError("Price cannot be 0")
        if qty + transaction.quantity < 0:
            raise InsufficientQuantityError("Insufficient quantity for this transaction")
        if transaction.transaction_date is None:
            transaction.transaction_date = date.today()
        return TransactionRepository.update_transaction(transaction_id, transaction)
    
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