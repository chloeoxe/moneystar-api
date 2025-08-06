from datetime import date
import pytest
from unittest.mock import patch
import pandas as pd
from model.transaction_model import Transaction
from service.portfolio_service import PortfolioService
from model.price_model import TickersLivePriceRequest, TickerPrice


class TestPortfolioService:
    @pytest.mark.anyio
    @patch(
        "repository.transaction_repository.TransactionRepository.get_all_transactions"
    )
    @patch("service.price_service.PriceService.fetch_live_prices")
    async def test_portfolio_calc(
        self, mock_fetch_live_prices, mock_get_all_transactions
    ):
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
                ticker="AAPL",
                name="Apple",
                quantity=-5,
                price=155.0,
                transaction_date=date(2025, 2, 1),
            ),
            Transaction(
                id="3",
                ticker="MSFT",
                name="Microsoft",
                quantity=20,
                price=250.0,
                transaction_date=date(2025, 1, 1),
            ),
        ]

        mock_fetch_live_prices.return_value = [
            TickerPrice(ticker="AAPL", date=date.today(), close=160.0),
            TickerPrice(ticker="MSFT", date=date.today(), close=260.0),
        ]

        result = await PortfolioService.portfolio_calc()

        mock_get_all_transactions.assert_called_once()
        mock_fetch_live_prices.assert_called_once_with(
            TickersLivePriceRequest(tickers=["AAPL", "MSFT"])
        )

        assert len(result) == 2
        assert result[0]["ticker"] == "AAPL"
        assert result[0]["live_price"] == 160.0
        assert result[0]["quantity"] == 5
        assert result[0]["pnl"] == 50
        assert result[1]["ticker"] == "MSFT"
        assert result[1]["live_price"] == 260.0
        assert result[1]["quantity"] == 20
        assert result[1]["pnl"] == 200

    @pytest.mark.anyio
    @patch(
        "repository.transaction_repository.TransactionRepository.get_all_transactions"
    )
    @patch("service.price_service.PriceService.fetch_live_prices")
    async def test_portfolio_calc_no_transactions(
        self, mock_fetch_live_prices, mock_get_all_transactions
    ):
        """Test portfolio_calc when no transactions are returned."""
        mock_get_all_transactions.return_value = []
        result = await PortfolioService.portfolio_calc()

        mock_get_all_transactions.assert_called_once()
        mock_fetch_live_prices.assert_not_called()
        assert result == []

    @pytest.mark.anyio
    @patch(
        "repository.transaction_repository.TransactionRepository.get_all_transactions"
    )
    @patch("service.price_service.PriceService.fetch_live_prices")
    async def test_portfolio_calc_partial_live_prices(
        self, mock_fetch_live_prices, mock_get_all_transactions
    ):
        """Test portfolio_calc when live prices are partially available."""
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
                ticker="GOOG",
                name="Google",
                quantity=5,
                price=2800.0,
                transaction_date=date(2025, 1, 1),
            ),
        ]

        mock_fetch_live_prices.return_value = [
            TickerPrice(ticker="AAPL", date=date.today(), close=160.0),
        ]

        result = await PortfolioService.portfolio_calc()

        mock_get_all_transactions.assert_called_once()
        mock_fetch_live_prices.assert_called_once_with(
            TickersLivePriceRequest(tickers=["AAPL", "GOOG"])
        )

        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"
        assert result[0]["live_price"] == 160.0
        assert result[0]["quantity"] == 10
        assert result[0]["pnl"] == 100

    @pytest.mark.anyio
    @patch("service.portfolio_service.PortfolioService.portfolio_calc")
    async def test_portfolio_summary(self, mock_portfolio_calc):
        # only mock the required columns
        mock_portfolio_calc.side_effect = [
            pd.DataFrame(
                [
                    {"ticker": "AAPL", "live_price": 160.0, "quantity": 5, "pnl": 50.0},
                    {
                        "ticker": "MSFT",
                        "live_price": 260.0,
                        "quantity": 20,
                        "pnl": 200.0,
                    },
                ]
            ),
            pd.DataFrame(
                [
                    {"ticker": "AAPL", "live_price": 150.0, "quantity": 5, "pnl": 0.0},
                    {"ticker": "MSFT", "live_price": 250.0, "quantity": 20, "pnl": 0.0},
                ]
            ),
        ]

        result = await PortfolioService.portfolio_summary()

        assert result["total_value"] == (160.0 * 5 + 260.0 * 20)
        assert result["monthly_pnl"] == (160.0 * 5 + 260.0 * 20) - (
            150.0 * 5 + 250.0 * 20
        )
        assert result["monthly_pnl_pct"] >= 4.34
        assert result["all_time_returns"] == 250.0
        assert result["all_time_returns_pct"] > 0

    @pytest.mark.anyio
    @patch("service.portfolio_service.PortfolioService.portfolio_calc")
    async def test_portfolio_summary_no_last_month_transactions(
        self, mock_portfolio_calc
    ):
        """Test portfolio_summary when there are no transactions for the last month."""
        mock_portfolio_calc.side_effect = [
            pd.DataFrame(
                [
                    {"ticker": "AAPL", "live_price": 160.0, "quantity": 5, "pnl": 50.0},
                    {
                        "ticker": "MSFT",
                        "live_price": 260.0,
                        "quantity": 20,
                        "pnl": 200.0,
                    },
                ]
            ),
            pd.DataFrame([]),
        ]

        result = await PortfolioService.portfolio_summary()

        # Assertions
        assert result["total_value"] == (160.0 * 5 + 260.0 * 20)
        assert result["monthly_pnl"] == result["total_value"]
        assert result["monthly_pnl_pct"] == 0
        assert result["all_time_returns"] == 250.0
        assert result["all_time_returns_pct"] > 0

    @pytest.mark.anyio
    @patch("service.portfolio_service.PortfolioService.portfolio_calc")
    async def test_portfolio_summary_no_current_month_transactions(
        self, mock_portfolio_calc
    ):
        mock_portfolio_calc.side_effect = [
            pd.DataFrame([]),
            pd.DataFrame(
                [
                    {"ticker": "AAPL", "live_price": 150.0, "quantity": 5, "pnl": 0.0},
                    {"ticker": "MSFT", "live_price": 250.0, "quantity": 20, "pnl": 0.0},
                ]
            ),
        ]

        result = await PortfolioService.portfolio_summary()

        assert result["total_value"] == 0
        assert result["monthly_pnl"] == -((150.0 * 5) + (250.0 * 20))
        assert result["monthly_pnl_pct"] == -100.0
        assert result["all_time_returns"] == 0
        assert result["all_time_returns_pct"] == 0
