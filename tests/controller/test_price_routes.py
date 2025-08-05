import pytest
from unittest.mock import patch, AsyncMock
from datetime import date
from controller.price_routes import get_historical_prices, get_live_prices_for_tickers, update_historical_prices
from model.price_model import TickersLivePriceRequest, TickerPrice, PriceUpdateRequest, PriceUpdateResponse
from fastapi import HTTPException

@pytest.mark.anyio
@patch("service.price_service.PriceService.get_historical_prices")
async def test_get_historical_prices(mock_get_historical_prices):
    """Test the get_historical_prices function."""
    mock_get_historical_prices.return_value = [
        TickerPrice(ticker="AAPL", date=date(2023, 1, 1), close=150.0),
        TickerPrice(ticker="MSFT", date=date(2023, 1, 1), close=250.0),
    ]

    result = await get_historical_prices()

    mock_get_historical_prices.assert_called_once()
    assert result == [
        TickerPrice(ticker="AAPL", date=date(2023, 1, 1), close=150.0),
        TickerPrice(ticker="MSFT", date=date(2023, 1, 1), close=250.0),
    ]

@pytest.mark.anyio
@patch("service.price_service.PriceService.get_historical_prices")
async def test_get_historical_prices_exception(mock_get_historical_prices):
    """Test the get_historical_prices function when an exception is raised."""
    mock_get_historical_prices.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await get_historical_prices()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Database error"
    mock_get_historical_prices.assert_called_once()

@pytest.mark.anyio
@patch("service.price_service.PriceService.fetch_live_prices", new_callable=AsyncMock)
async def test_get_live_prices_for_tickers(mock_fetch_live_prices):
    """Test the get_live_prices_for_tickers function."""
    mock_request = TickersLivePriceRequest(
        tickers=["AAPL", "MSFT"], target_date="2023-01-01", interval="1d"
    )
    mock_fetch_live_prices.return_value = [
        TickerPrice(ticker="AAPL", date=date(2023, 1, 1), close=150.0),
        TickerPrice(ticker="MSFT", date=date(2023, 1, 1), close=250.0),
    ]

    result = await get_live_prices_for_tickers(mock_request)

    mock_fetch_live_prices.assert_called_once_with(mock_request)
    assert result == [
        TickerPrice(ticker="AAPL", date=date(2023, 1, 1), close=150.0),
        TickerPrice(ticker="MSFT", date=date(2023, 1, 1), close=250.0),
    ]

@pytest.mark.anyio
@patch("service.price_service.PriceService.update_prices", new_callable=AsyncMock)
async def test_update_historical_prices(mock_update_prices):
    """Test the update_historical_prices function."""
    mock_request = PriceUpdateRequest(
        years_to_keep=5,
        months_before_earliest=3,
    )
    mock_update_prices.return_value = PriceUpdateResponse(
            tickers_updated=["AAPL", "MSFT"],
            total_new_prices_added=15,
            total_old_prices_deleted=20,
            update_details={"AAPL": 10, "MSFT": 5},
        )

    result = await update_historical_prices(mock_request)

    mock_update_prices.assert_called_once_with(mock_request)
    assert result.model_dump() == {
        "tickers_updated": ["AAPL", "MSFT"],
        "total_new_prices_added": 15,
        "total_old_prices_deleted": 20,
        "update_details": {"AAPL": 10, "MSFT": 5},
    }
