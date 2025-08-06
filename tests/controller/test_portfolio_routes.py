from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from controller.portfolio_routes import router

client = TestClient(router)

class TestPortfolioRoutes:
    
    @patch("service.portfolio_service.PortfolioService.portfolio_summary")
    def test_get_portfolio_summary(self, mock_get_portfolio_summary): 
        "Test success"
        
        mock_data = {
            "total_value": 12000.50,
            "total_value_pct": 5.25,
            "monthly_pnl": 500.00,
            "monthly_pnl_pct": 2.10,
            "all_time_returns": 1500.75,
            "all_time_returns_pct": 15.0,
            "cash": 2500.00,
            "cash_pct": 20.83,
            "invested_val": 30000.0,
            "invested_val_pct": 10.0,
        }
        mock_get_portfolio_summary.return_value = mock_data
        
        response = client.get("/summary")
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_portfolio_summary.assert_called_once()
        
    @patch("service.portfolio_service.PortfolioService.portfolio_summary")
    def test_get_portfolio_summary_exception(self, mock_get_portfolio_summary):
        "Test Exception"
        
        exception_msg = "Failed to retrieve portfolio summary"
        mock_get_portfolio_summary.side_effect = Exception(exception_msg)
        
        with pytest.raises(HTTPException) as exc_info:      
            client.get("/summary")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_msg
        mock_get_portfolio_summary.assert_called_once()
        
    @patch("service.portfolio_service.PortfolioService.portfolio_calc")
    def test_get_portfolio_calc(self, mock_get_portfolio): 
        "Test success"
        
        mock_data = [{"id":"0","ticker":"AAPL","name":"Apple Inc.","quantity":164,"avg_price":167.0639179286761,"live_price":202.93,"price_delta":35.866082071323916,"pct_delta":21.46847896063115,"pnl":5882.037459697122},{"id":"1","ticker":"AMD","name":"Advanced Micro Devices Inc.","quantity":231,"avg_price":103.16853805990657,"live_price":174.38,"price_delta":71.21146194009343,"pct_delta":69.02439763054826,"pnl":16449.847708161582}]
        mock_get_portfolio.return_value = mock_data
        
        response = client.get("/portfolio")
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_portfolio.assert_called_once()
        
    @patch("service.portfolio_service.PortfolioService.portfolio_calc")
    def test_get_portfolio_calc_exception(self, mock_get_portfolio):
        "Test Exception"
        
        exception_msg = "Failed to retrieve portfolio calculations"
        mock_get_portfolio.side_effect = Exception(exception_msg)
        
        with pytest.raises(HTTPException) as exc_info:      
            client.get("/portfolio")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_msg
        mock_get_portfolio.assert_called_once()