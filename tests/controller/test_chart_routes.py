from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from controller.chart_routes import router

client = TestClient(router)

class TestChartRoutes: 
    
    @patch("service.chart_service.ChartService.get_portfolio_linechart_data")
    def test_get_portfolio_linechart_data(self, mock_get_portfolio_linechart_data): 
        "Test success"
        
        mock_data = {"labels": ["Jan", "Feb", "Mar"], "data": [100, 120, 110]}
        mock_get_portfolio_linechart_data.return_value = mock_data
        
        response = client.get("/charts/portfolio-linechart")
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_portfolio_linechart_data.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_portfolio_linechart_data")
    def test_get_portfolio_linechart_data_exception(self, mock_get_portfolio_linechart_data):
        "Test Exception"
        
        exception_msg = "Failed to retrieve line chart data"
        mock_get_portfolio_linechart_data.side_effect = Exception(exception_msg)
        
        with pytest.raises(HTTPException) as exc_info:      
            client.get("/charts/portfolio-linechart")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_msg
        mock_get_portfolio_linechart_data.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_portfolio_distribution_data")
    def test_get_portfolio_piechart(self, mock_get_portfolio_piechart): 
        "Test success"
        
        mock_data = {"labels": ["Jan", "Feb", "Mar"], "data": [100, 120, 110]}
        mock_get_portfolio_piechart.return_value = mock_data
        
        response = client.get("/charts/portfolio-piechart")
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_portfolio_piechart.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_portfolio_distribution_data")
    def test_get_portfolio_piechart_exception(self, mock_get_portfolio_piechart):
        "Test Exception"
        
        exception_msg = "Failed to retrieve pie chart data"
        mock_get_portfolio_piechart.side_effect = Exception(exception_msg)
        
        with pytest.raises(HTTPException) as exc_info:      
            client.get("/charts/portfolio-piechart")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_msg
        mock_get_portfolio_piechart.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_top_holdings_performance_data")
    def test_get_portfolio_barchart(self, mock_get_portfolio_barchart): 
        "Test success"
        
        mock_data = {"labels": ["Jan", "Feb", "Mar"], "data": [100, 120, 110]}
        mock_get_portfolio_barchart.return_value = mock_data
        
        response = client.get("/charts/portfolio-barchart")
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_portfolio_barchart.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_top_holdings_performance_data")
    def test_get_portfolio_barchart_exception(self, mock_get_portfolio_barchart):
        "Test Exception"
        
        exception_msg = "Failed to retrieve bar chart data"
        mock_get_portfolio_barchart.side_effect = Exception(exception_msg)
        
        with pytest.raises(HTTPException) as exc_info:      
            client.get("/charts/portfolio-barchart")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_msg
        mock_get_portfolio_barchart.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_overall_portfolio_month_change")
    def test_get_portfolio_month_change(self, mock_get_portfolio_month_change): 
        "Test success"
        
        mock_data = {"labels": ["Jan", "Feb", "Mar"], "data": [100, 120, 110]}
        mock_get_portfolio_month_change.return_value = mock_data
        
        response = client.get("/charts/portfolio-overall-month-change")
        
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get_portfolio_month_change.assert_called_once()
        
    @patch("service.chart_service.ChartService.get_overall_portfolio_month_change")
    def test_get_portfolio_month_change_exception(self, mock_get_portfolio_month_change):
        "Test Exception"
        
        exception_msg = "Failed to retrieve overall month change data"
        mock_get_portfolio_month_change.side_effect = Exception(exception_msg)
        
        with pytest.raises(HTTPException) as exc_info:      
            client.get("/charts/portfolio-overall-month-change")
            
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == exception_msg
        mock_get_portfolio_month_change.assert_called_once()
        
    