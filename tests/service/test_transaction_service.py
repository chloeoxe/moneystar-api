import pytest
from datetime import date
from unittest.mock import patch
import pandas as pd

from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate
from repository.transaction_repository import TransactionRepository
from service.transaction_service import TransactionService

class TestTransactionService: 
    @patch('repository.transaction_repository.TransactionRepository.get_all_transactions')
    def test_get_all_transactions(self, mock_get_all_transactions):
        """Test fetching all transactions successfully."""
        
        mock_transactions = [
            Transaction(id="1", ticker="APPL", name="Apple Inc.", transaction_date=date(2023, 1, 1), quantity=10, price=100.0),
            Transaction(id="2", ticker="GOOG", name="Alphabet Inc.", transaction_date=date(2023, 1, 2), quantity=-5, price=50.0)
        ]
        mock_get_all_transactions.return_value = mock_transactions

        result = TransactionService.get_all_transactions()

        mock_get_all_transactions.assert_called_once()
        assert result == mock_transactions
        
    @patch('repository.transaction_repository.TransactionRepository.create_transaction')
    def test_create_transaction_success_with_date_provided(self, mock_create_transaction):
        """Test creating a transaction successfully when a date is explicitly provided."""
        
        transaction_date_str = "2023-01-15"
        transaction_create = TransactionCreate(ticker="MSFT", name="Microsoft Corp.", quantity=10, price=100.0, transaction_date=transaction_date_str)
        expected_result = {"id": "new_id", "message": "Transaction created successfully"}
        mock_create_transaction.return_value = expected_result
        
        result = TransactionService.create_transaction(transaction_create)

        mock_create_transaction.assert_called_once_with(transaction_create)
        assert result == expected_result
        
    @patch('repository.transaction_repository.TransactionRepository.create_transaction')
    def test_create_transaction_success_with_date_none(self, mock_create_transaction):
        """Test creating a transaction when transaction_date is None."""
        
        transaction_create_original = TransactionCreate(ticker="MSFT", name="Microsoft Corp.", quantity=10, price=100.0, transaction_date=None)
        expected_result = {"id": "new_id", "message": "Transaction created successfully"}
        mock_create_transaction.return_value = expected_result

        result = TransactionService.create_transaction(transaction_create_original)

        mock_create_transaction.assert_called_once_with(transaction_create_original)
        assert result == expected_result
        
    @patch('repository.transaction_repository.TransactionRepository.create_transaction')
    def test_create_transaction_quantity_zero_raises_error(self, mock_create_transaction):
        """Test that creating a transaction with quantity 0 raises an error."""
        transaction_create = TransactionCreate(ticker="MSFT", name="Microsoft Corp.", transaction_date="2023-01-01", quantity=0, price=100.0)

        with pytest.raises(Exception) as excinfo:
            TransactionService.create_transaction(transaction_create)
        assert "Quantity cannot be 0" in str(excinfo.value)
        mock_create_transaction.assert_not_called()
        
    @patch('repository.transaction_repository.TransactionRepository.create_transaction')
    def test_create_transaction_price_zero_raises_error(self, mock_create_transaction):
        """Test that creating a transaction with price 0 raises an error."""
        
        transaction_create = TransactionCreate(ticker="MSFT", name="Microsoft Corp.", transaction_date="2023-01-01", quantity=10, price=0)

        with pytest.raises(Exception) as excinfo:
            TransactionService.create_transaction(transaction_create)
        assert "Price cannot be 0" in str(excinfo.value)
        mock_create_transaction.assert_not_called()
        
    @patch('repository.transaction_repository.TransactionRepository.update_transaction')
    def test_update_transaction_success(self, mock_update_transaction):
        """Test updating a transaction successfully."""
        
        transaction_id = "some_id"
        transaction_update = TransactionUpdate(quantity=20, price=200.0, ticker="AMZN")
        expected_result = {"id": transaction_id, "message": "Transaction updated successfully"}
        mock_update_transaction.return_value = expected_result

        result = TransactionService.update_transaction(transaction_id, transaction_update)

        mock_update_transaction.assert_called_once_with(transaction_id, transaction_update)
        assert result == expected_result
        
    @patch('repository.transaction_repository.TransactionRepository.update_transaction')
    def test_update_transaction_quantity_zero_raises_error(self, mock_update_transaction):
        """Test that updating a transaction with quantity 0 raises an error."""

        transaction_id = "some_id"
        transaction_update = TransactionUpdate(quantity=0, price=200.0)

        with pytest.raises(Exception) as excinfo:
            TransactionService.update_transaction(transaction_id, transaction_update)
        assert "Quantity cannot be 0" in str(excinfo.value)
        mock_update_transaction.assert_not_called()

    @patch('repository.transaction_repository.TransactionRepository.update_transaction')
    def test_update_transaction_price_zero_raises_error(self, mock_update_transaction):
        """Test that updating a transaction with price 0 raises an error."""
        
        transaction_id = "some_id"
        transaction_update = TransactionUpdate(quantity=10, price=0)

        with pytest.raises(Exception) as excinfo:
            TransactionService.update_transaction(transaction_id, transaction_update)
        assert "Price cannot be 0" in str(excinfo.value)
        mock_update_transaction.assert_not_called()
        
        
    @patch('repository.transaction_repository.TransactionRepository.delete_transaction_by_id')
    def test_delete_transaction_by_id_success(self, mock_delete_transaction_by_id):
        """Test deleting a transaction successfully by ID."""

        transaction_id = "some_id"
        expected_result = {"message": f"Transaction with ID {transaction_id} deleted successfully"}
        mock_delete_transaction_by_id.return_value = expected_result

        result = TransactionService.delete_transaction_by_id(transaction_id)

        mock_delete_transaction_by_id.assert_called_once_with(transaction_id)
        assert result == expected_result

    @patch('repository.transaction_repository.TransactionRepository.delete_transaction_by_id')
    def test_delete_transaction_by_id_empty_id_raises_error(self, mock_delete_transaction_by_id):
        """Test that deleting a transaction with an empty ID raises an error."""
        
        transaction_id = ""

        with pytest.raises(Exception) as excinfo:
            TransactionService.delete_transaction_by_id(transaction_id)
        assert "Transaction ID cannot be empty" in str(excinfo.value)
        mock_delete_transaction_by_id.assert_not_called()

    @patch('repository.transaction_repository.TransactionRepository.get_all_transactions')
    def test_get_transaction_table_data_empty(self, mock_get_all_transactions):
        """Test fetching table data when no transactions exist."""

        mock_get_all_transactions.return_value = []

        result = TransactionService.get_transaction_table_data()

        mock_get_all_transactions.assert_called_once()
        assert result == []

    @patch('repository.transaction_repository.TransactionRepository.get_all_transactions')
    def test_get_transaction_table_data_with_data(self, mock_get_all_transactions):
        """Test fetching and formatting transaction data for the table."""

        mock_transactions = [
            Transaction(id="1", ticker="MSFT", name="Microsoft Corp.", transaction_date=date(2023, 5, 10), quantity=5, price=100.0),
            Transaction(id="2", ticker="TSLA", name="Tesla Inc.", transaction_date=date(2023, 5, 11), quantity=-2, price=200.0),
            Transaction(id="3", ticker="AMZN", name="Amazon.com Inc.", transaction_date=date(2023, 5, 12), quantity=15, price=50.0),
        ]
        mock_get_all_transactions.return_value = mock_transactions

        result = TransactionService.get_transaction_table_data()

        mock_get_all_transactions.assert_called_once()
        expected_result = [
            {'id': '1', 'ticker': 'MSFT', 'name': 'Microsoft Corp.', 'transaction_date': date(2023, 5, 10), 'quantity': 5, 'price': 100.0, 'buy_sell': 'Buy'},
            {'id': '2', 'ticker': 'TSLA', 'name': 'Tesla Inc.', 'transaction_date': date(2023, 5, 11), 'quantity': -2, 'price': 200.0, 'buy_sell': 'Sell'},
            {'id': '3', 'ticker': 'AMZN', 'name': 'Amazon.com Inc.', 'transaction_date': date(2023, 5, 12), 'quantity': 15, 'price': 50.0, 'buy_sell': 'Buy'},
        ]
        assert result == expected_result