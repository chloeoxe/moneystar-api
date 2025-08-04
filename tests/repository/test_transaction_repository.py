from unittest.mock import patch
import pytest
from repository.transaction_repository import TransactionRepository


class TestTransactionRepository:
    def test_get_all_transactions_empty_db(self, clean_table_client):
        transactions = TransactionRepository.get_all_transactions()
        assert transactions == []
