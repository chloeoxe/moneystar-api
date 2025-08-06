from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import date

from controller.transaction_routes import router
from model.transaction_model import Transaction, TransactionCreate, TransactionUpdate

client = TestClient(router)

class TestTransactionRoutes: 
    
    @patch('service.transaction_service.TransactionService.get_all_transactions')
    def test_get_all_transactions(self, mock_get_all_transactions):
        "Test GET/ transactions successfully. "
        
        mock_data = [
            Transaction(id="1", ticker="APPL", name="Apple Inc.", transaction_date=date(2023, 1, 1), quantity=10, price=100.0),
            Transaction(id="2", ticker="GOOG", name="Alphabet Inc.", transaction_date=date(2023, 1, 2), quantity=-5, price=50.0)
        ]
        mock_get_all_transactions.return_value = mock_data
        
        response = client.get("/transactions")
        
        assert response.status_code == 200
        
        expected_json = [t.model_dump() for t in mock_data]
        for item in expected_json:
            if isinstance(item.get("transaction_date"), date):
                item["transaction_date"] = item["transaction_date"].isoformat()
        assert response.json() == expected_json
        mock_get_all_transactions.assert_called_once()
        
    @patch('service.transaction_service.TransactionService.get_all_transactions')
    def test_get_all_transactions_exception(self, mock_get_all_transactions):
        "Test GET/ transactions with HTTPException Error."
        
        mock_get_all_transactions.side_effect = Exception("Database connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            client.get("/transactions")
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Database connection failed"
        mock_get_all_transactions.assert_called_once()
        
    @patch('service.transaction_service.TransactionService.create_transaction')
    def test_create_transaction(self, mock_create_transaction):
        "Test POST/ transaction successfully."
        
        transaction_data = {
            "ticker": "GOOG",
            "name": "Alphabet Inc.",
            "quantity": 10,
            "price": 1000.0,
            "transaction_date": "2024-07-20"
        }
        mock_service_response = {
            "id": "abc-123",
            "ticker": "GOOG",
            "name": "Alphabet Inc.",
            "quantity": 10,
            "price": 1000.0,
            "transaction_date": date(2024, 7, 20).isoformat()
        }
        mock_create_transaction.return_value = mock_service_response

        response = client.post("/transaction", json=transaction_data)

        assert response.status_code == 200
        assert response.json() == mock_service_response
        expected_transaction_create = TransactionCreate(**transaction_data)
        mock_create_transaction.assert_called_once_with(expected_transaction_create)
        
    @patch('service.transaction_service.TransactionService.create_transaction')
    def test_create_transaction_value_error(self, mock_create_transaction):
        "Test POST/ transactions with ValueError."
        transaction_data = {
            "ticker": "GOOG",
            "name": "Alphabet Inc.",
            "quantity": 0,
            "price": 1000.0,
            "transaction_date": "2024-07-20"
        }
        exception_message = "Quantity cannot be 0" # Use variable
        mock_create_transaction.side_effect = ValueError(exception_message)
        
        with pytest.raises(HTTPException) as exc_info:
            client.post("/transaction", json=transaction_data)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_message
        mock_create_transaction.assert_called_once()
        
    @patch('service.transaction_service.TransactionService.create_transaction')
    def test_create_transaction_http_exception(self, mock_create_transaction):
        "Test POST/ transactions with HTTPException."
        transaction_data = {
            "ticker": "GOOG",
            "name": "Alphabet Inc.",
            "quantity": 0,
            "price": 1000.0,
            "transaction_date": "2024-07-20"
        }
        
        exception_message = "Unknown service error"
        mock_create_transaction.side_effect = Exception(exception_message)
        
        with pytest.raises(HTTPException) as exc_info:
            client.post("/transaction", json=transaction_data)
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_message
        mock_create_transaction.assert_called_once()
        
    @patch('service.transaction_service.TransactionService.update_transaction')
    def test_update_transaction(self, mock_update_transaction):
        "Test PUT/ transactions successfully."
        transaction_id = "test-id-123"
        update_data = {
            "quantity": 15,
            "price": 160.0,
            "transaction_date": "2023-01-05"
        }
        mock_service_response = {
            "id": transaction_id,
            "ticker": "APPL",
            "name": "Apple Inc.",
            "quantity": 15,
            "price": 160.0,
            "transaction_date": date(2023, 1, 5).isoformat()
        }
        
        mock_update_transaction.return_value = mock_service_response
        
        response = client.put(f"/transaction/{transaction_id}", json=update_data)
        
        assert response.status_code == 200
        assert response.json() == mock_service_response
        expected_transaction_update = TransactionUpdate(**update_data)
        mock_update_transaction.assert_called_once_with(transaction_id, expected_transaction_update)
        
    @patch('service.transaction_service.TransactionService.update_transaction')
    def test_update_transaction_value_error(self, mock_update_transaction):
        "Test PUT/ transactions with ValueError."
        transaction_id = "test-id-123"
        update_data = {
            "quantity": 15,
            "price": 160.0,
            "transaction_date": "2023-01-05"
        }
        
        exception_message = "Internal update error"
        mock_update_transaction.side_effect = ValueError(exception_message)
        
        with pytest.raises(HTTPException) as exc_info:
            client.put(f"/transaction/{transaction_id}", json=update_data)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == exception_message
        mock_update_transaction.assert_called_once()
        
    @patch('service.transaction_service.TransactionService.delete_transaction_by_id')
    def test_delete_transaction(self, mock_delete_transaction):
        "Test DELETE/ transaction  with success."
        transaction_id = "test-id-123"
        mock_delete_transaction.return_value = {"message": f"Transaction with id={transaction_id} deleted successfully"}
        
        response = client.delete(f'/transaction/{transaction_id}')
        
        assert response.status_code == 200
        assert response.json() == {"message": f"Transaction with id={transaction_id} deleted successfully"}
        mock_delete_transaction.assert_called_once_with(transaction_id)
        
    @patch('service.transaction_service.TransactionService.delete_transaction_by_id')
    def test_delete_transaction_with_value_error(self, mock_delete_transaction):
        "Test DELETE/ transaction with HTTPException"
        transaction_id = "test-id-123"
        exception_message = f"Transaction with id={transaction_id} not found"
        mock_delete_transaction.side_effect = Exception(exception_message)
        
        with pytest.raises(Exception) as exc_info: 
            client.delete(f'/transaction/{transaction_id}')
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_message
        mock_delete_transaction.assert_called_once_with(transaction_id)
    
    @patch('service.transaction_service.TransactionService.get_transaction_table_data')
    def test_get_transaction_table_data(self, mock_get_transaction_table_data):
        "Test GET/ transaction table data successfully"
        
        mock_data = [
            {'id': '1', 'ticker': 'APPL', 'name': 'Apple Inc.', 'transaction_date': date(2023, 1, 1).isoformat(), 'quantity': 10, 'price': 150.0, 'buy_sell': 'Buy'},
            {'id': '2', 'ticker': 'MSFT', 'name': 'Microsoft Corp.', 'transaction_date': date(2023, 1, 2).isoformat(), 'quantity': -5, 'price': 200.0, 'buy_sell': 'Sell'},
        ]
        
        mock_get_transaction_table_data.return_value = mock_data
        
        response = client.get('/transactions-table')
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_transaction_table_data.assert_called_once()
        
    @patch('service.transaction_service.TransactionService.get_transaction_table_data')
    def test_get_transaction_table_data_exception(self, mock_get_transaction_table_data):
        exception_message = "Data table processing error" 
        mock_get_transaction_table_data.side_effect = Exception(exception_message)
        
        with pytest.raises(Exception) as exc_info: 
            response = client.get('/transactions-table')
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_message
        mock_get_transaction_table_data.assert_called_once()