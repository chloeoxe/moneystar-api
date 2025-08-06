import pytest
from datetime import date
from dateutil.relativedelta import relativedelta
from unittest.mock import patch
import pandas as pd

from model.price_model import TickerPrice, TickerPriceUpdateResponse
from service.price_service import PriceService
from datetime import date, timedelta
from model.price_model import (
    TickerPrice,
    TickersLivePriceRequest,
    TickerPriceUpdateRequest,
    PriceUpdateRequest,
)


class TestPriceService:
    @patch("repository.price_repository.PriceRepository.get_all_prices")
    def test_get_historical_prices(self, mock_get_historical_prices):
        """Test fetching all prices successfully."""
        mock_prices = [
            TickerPrice(ticker="APPL", date=date(2023, 1, 1), close=1),
        ]
        mock_get_historical_prices.return_value = mock_prices
        result = PriceService.get_historical_prices()

        mock_get_historical_prices.assert_called_once()
        assert result == mock_prices

    @pytest.mark.anyio
    @patch("yfinance.download")
    async def test_fetch_live_prices(self, mock_yfinance_download):
        """Test fetching live prices using yfinance with a valid response."""
        mock_request = TickersLivePriceRequest(
            tickers=["AAPL", "MSFT"], target_date="2023-01-01", interval="1d"
        )
        mock_yfinance_download.return_value = pd.DataFrame(
            {
                ("Close", "AAPL"): [150.0],
                ("Close", "MSFT"): [250.0],
            },
            index=pd.to_datetime(["2023-01-01"]),
        )

        result = await PriceService.fetch_live_prices(mock_request)

        mock_yfinance_download.assert_called_once_with(
            tickers=["AAPL", "MSFT"],
            start="2022-12-27",
            end="2023-01-02",
            interval="1d",
            progress=False,
            threads=True,
            auto_adjust=True,
        )
        assert len(result) == 2
        assert result[0].ticker == "AAPL"
        assert result[0].date == date(2023, 1, 1)
        assert result[0].close == 150.0
        assert result[1].ticker == "MSFT"
        assert result[1].date == date(2023, 1, 1)
        assert result[1].close == 250.0

    @pytest.mark.anyio
    @patch("yfinance.download")
    async def test_fetch_live_prices_no_data(self, mock_yfinance_download):
        """Test fetching live prices when no data is returned."""
        mock_request = TickersLivePriceRequest(
            tickers=["AAPL"], target_date="2023-01-01", interval="1d"
        )
        mock_yfinance_download.return_value = pd.DataFrame()

        result = await PriceService.fetch_live_prices(mock_request)

        mock_yfinance_download.assert_called_once()
        assert len(result) == 0

    @pytest.mark.anyio
    @patch("yfinance.download")
    async def test_fetch_live_prices_partial_data(self, mock_yfinance_download):
        """Test fetching live prices when partial data is returned."""
        mock_request = TickersLivePriceRequest(
            tickers=["AAPL", "MSFT"], target_date="2023-01-01", interval="1d"
        )
        mock_yfinance_download.return_value = pd.DataFrame(
            {
                ("Close", "AAPL"): [150.0],
            },
            index=pd.to_datetime(["2023-01-01"]),
        )

        result = await PriceService.fetch_live_prices(mock_request)

        mock_yfinance_download.assert_called_once()
        assert len(result) == 2
        assert result[0].ticker == "AAPL"
        assert result[0].date == date(2023, 1, 1)
        assert result[0].close == 150.0
        assert result[1].ticker == "MSFT"
        assert result[1].date is None
        assert result[1].close is None

    @pytest.mark.anyio
    @patch("yfinance.download")
    async def test_fetch_live_prices_exception(self, mock_yfinance_download):
        """Test fetching live prices when an exception is raised."""
        mock_request = TickersLivePriceRequest(
            tickers=["AAPL"], target_date="2023-01-01", interval="1d"
        )
        mock_yfinance_download.side_effect = Exception("Download failed")

        with pytest.raises(
            Exception,
            match=r"\[yfinance\] Live prices batch request failed: Download failed",
        ):
            await PriceService.fetch_live_prices(mock_request)

        mock_yfinance_download.assert_called_once()

    @pytest.mark.anyio
    @patch("yfinance.download")
    async def test_fetch_missing_prices(self, mock_yfinance_download):
        """Test fetching missing prices with valid data."""
        mock_ticker = "AAPL"
        mock_missing_dates = [date(2023, 1, 1), date(2023, 1, 2)]
        mock_yfinance_download.return_value = pd.DataFrame(
            {
                "Close": [150.0, 155.0],
            },
            index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
        )

        result = await PriceService.fetch_missing_prices(
            mock_ticker, mock_missing_dates
        )

        mock_yfinance_download.assert_called_once_with(
            mock_ticker,
            start=min(mock_missing_dates),
            end=max(mock_missing_dates) + timedelta(days=1),
            progress=False,
            auto_adjust=True,
        )
        assert len(result) == 2
        assert result[0].ticker == "AAPL"
        assert result[0].date == date(2023, 1, 1)
        assert result[0].close == 150.0
        assert result[1].ticker == "AAPL"
        assert result[1].date == date(2023, 1, 2)
        assert result[1].close == 155.0

    @pytest.mark.anyio
    @patch("yfinance.download")
    async def test_fetch_missing_prices_exception(self, mock_yfinance_download):
        """Test fetching missing prices when an exception is raised."""
        mock_ticker = "AAPL"
        mock_missing_dates = [date(2023, 1, 1), date(2023, 1, 2)]
        mock_yfinance_download.side_effect = Exception("Download failed")

        with pytest.raises(Exception, match="Download failed"):
            await PriceService.fetch_missing_prices(mock_ticker, mock_missing_dates)

        mock_yfinance_download.assert_called_once()

    @pytest.mark.anyio
    @patch("service.price_service.PriceService.get_market_open_dates")
    @patch("repository.price_repository.PriceRepository.get_existing_dates_per_ticker")
    @patch("service.price_service.PriceService.fetch_missing_prices")
    @patch("repository.price_repository.PriceRepository.upsert_prices")
    async def test_update_prices_for_ticker(
        self,
        mock_upsert_prices,
        mock_fetch_missing_prices,
        mock_get_existing_dates_per_ticker,
        mock_get_market_open_dates,
    ):
        """Test updating prices for a specific ticker."""
        mock_request = TickerPriceUpdateRequest(
            ticker="AAPL",
            earliest_buy_date=date(2022, 1, 1),
            years_to_keep=2,
            months_before_earliest=3,
        )
        mock_get_market_open_dates.return_value = [date(2022, 1, 1), date(2022, 1, 2)]
        mock_get_existing_dates_per_ticker.return_value = [date(2022, 1, 1)]
        mock_fetch_missing_prices.return_value = [
            TickerPrice(ticker="AAPL", date=date(2022, 1, 2), close=150.0)
        ]
        mock_upsert_prices.return_value = 1

        result = await PriceService.update_prices_for_ticker(mock_request)

        mock_get_market_open_dates.assert_called_once()
        mock_get_existing_dates_per_ticker.assert_called_once_with(
            "AAPL", date.today() - relativedelta(years=2)
        )
        mock_fetch_missing_prices.assert_called_once_with("AAPL", [date(2022, 1, 2)])
        mock_upsert_prices.assert_called_once()

        assert result.ticker == "AAPL"
        assert result.missing_dates_fetched == 1

    @pytest.mark.anyio
    @patch(
        "repository.transaction_repository.TransactionRepository.get_buy_transactions"
    )
    @patch("repository.price_repository.PriceRepository.delete_prices_older_than_date")
    @patch("service.price_service.PriceService.update_prices_for_ticker")
    async def test_update_prices(
        self,
        mock_update_prices_for_ticker,
        mock_delete_prices_older_than_date,
        mock_get_buy_transactions,
    ):
        """Test updating prices for all tickers."""

        mock_request = PriceUpdateRequest(years_to_keep=2, months_before_earliest=3)
        mock_get_buy_transactions.return_value = [
            {"ticker": "AAPL", "transaction_date": "2022-01-01"},
            {"ticker": "MSFT", "transaction_date": "2022-02-01"},
        ]
        mock_update_prices_for_ticker.side_effect = [
            TickerPriceUpdateResponse(ticker="AAPL", missing_dates_fetched=2),
            TickerPriceUpdateResponse(ticker="MSFT", missing_dates_fetched=3),
        ]
        mock_delete_prices_older_than_date.return_value = 5

        result = await PriceService.update_prices(mock_request)

        mock_get_buy_transactions.assert_called_once()
        mock_update_prices_for_ticker.assert_any_call(
            TickerPriceUpdateRequest(
                ticker="AAPL",
                earliest_buy_date=date(2022, 1, 1),
                years_to_keep=2,
                months_before_earliest=3,
            )
        )
        mock_update_prices_for_ticker.assert_any_call(
            TickerPriceUpdateRequest(
                ticker="MSFT",
                earliest_buy_date=date(2022, 2, 1),
                years_to_keep=2,
                months_before_earliest=3,
            )
        )
        mock_delete_prices_older_than_date.assert_called_once()

        assert result.tickers_updated == ["AAPL", "MSFT"]
        assert result.total_new_prices_added == 5
        assert result.total_old_prices_deleted == 5
        assert result.update_details == {"AAPL": 2, "MSFT": 3}
