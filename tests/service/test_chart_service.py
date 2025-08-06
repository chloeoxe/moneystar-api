from datetime import date
import pytest
from unittest.mock import patch
import pandas as pd
from model.transaction_model import Transaction
from service.chart_service import ChartService
from model.price_model import TickerPrice


class TestChartService:
    @pytest.mark.anyio
    @patch(
        "repository.transaction_repository.TransactionRepository.get_all_transactions"
    )
    @patch("service.price_service.PriceService.fetch_live_prices")
    async def test_get_all_portfolio_prices_and_values(
        self, mock_fetch_live_prices, mock_get_all_transactions
    ):
        """Test get_all_portfolio_prices_and_values."""
        mock_get_all_transactions.return_value = [
            Transaction(
                id="1",
                ticker="AAPL",
                name="Apple",
                quantity=10,
                price=150.0,
                transaction_date=date(2025, 1, 1),
            ),
            Transaction(
                id="2",
                ticker="MSFT",
                name="Microsoft",
                quantity=20,
                price=250.0,
                transaction_date=date(2025, 1, 1),
            ),
        ]
        mock_fetch_live_prices.return_value = [
            TickerPrice(ticker="AAPL", close=160.0, date=date(2025, 1, 1)),
            TickerPrice(ticker="MSFT", close=260.0, date=date(2025, 1, 1)),
        ]
        result = await ChartService.get_all_portfolio_prices_and_values()

        assert not result.empty
        assert len(result) == 2
        assert result.loc[result["ticker"] == "AAPL", "price"].iloc[0] == 160.0
        assert result.loc[result["ticker"] == "MSFT", "price"].iloc[0] == 260.0
        assert result.loc[result["ticker"] == "AAPL", "value"].iloc[0] == 1600.0
        assert result.loc[result["ticker"] == "MSFT", "value"].iloc[0] == 5200.0

    @pytest.mark.anyio
    @patch("service.chart_service.ChartService.get_all_portfolio_prices_and_values")
    async def test_get_portfolio_distribution_data(
        self, mock_get_all_portfolio_prices_and_values
    ):
        """Test get_portfolio_distribution_data."""
        # mock only required columns
        mock_get_all_portfolio_prices_and_values.return_value = pd.DataFrame(
            [
                {"ticker": "AAPL", "value": 1600.0},
                {"ticker": "MSFT", "value": 5200.0},
                {"ticker": "GOOG", "value": 3000.0},
                {"ticker": "AMZN", "value": 2000.0},
                {"ticker": "TSLA", "value": 1000.0},
                {"ticker": "NFLX", "value": 500.0},
            ]
        )
        result = await ChartService.get_portfolio_distribution_data()

        assert len(result) == 6
        assert result[-1]["ticker"] == "Others"
        assert result[-1]["value"] == 500.0

    @pytest.mark.anyio
    @patch(
        "service.chart_service.ChartService.get_all_portfolio_prices_and_values_including_last_month"
    )
    async def test_get_top_holdings_performance_data(
        self, mock_get_all_portfolio_prices_and_values_including_last_month
    ):
        """Test get_top_holdings_performance_data."""
        mock_get_all_portfolio_prices_and_values_including_last_month.return_value = (
            pd.DataFrame(
                [
                    {
                        "ticker": "AAPL",
                        "price": 160.0,
                        "prev_price": 150.0,
                        "quantity": 10,
                        "value": 1600.0,
                    },
                    {
                        "ticker": "MSFT",
                        "price": 260.0,
                        "prev_price": 250.0,
                        "quantity": 20,
                        "value": 5200.0,
                    },
                    {
                        "ticker": "GOOG",
                        "price": 3000.0,
                        "prev_price": 2900.0,
                        "quantity": 1,
                        "value": 3000.0,
                    },
                ]
            )
        )

        result = await ChartService.get_top_holdings_performance_data()

        assert len(result) == 3
        assert result[0]["ticker"] == "MSFT"
        assert result[0]["fixed_change"] == 10.0
        assert result[0]["percentage_change"] == 4.0
        assert result[1]["ticker"] == "GOOG"
        assert result[1]["fixed_change"] == 100.0
        assert result[1]["percentage_change"] == 3.45
        assert result[2]["ticker"] == "AAPL"
        assert result[2]["fixed_change"] == 10.0
        assert result[2]["percentage_change"] == 6.67
