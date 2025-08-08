from yfinance import Ticker
from model.watchlist_model import WatchlistResponse
from repository.watchlist_repository import WatchlistRepository

class WatchlistService:

    @staticmethod
    def fetch_watchlist_data():
        tickers = WatchlistRepository.get_all_tickers()
        results = []

        for t in tickers:
            stock = Ticker(t).info
            results.append(WatchlistResponse(
                ticker=t,
                price=stock.get("regularMarketPrice", 0.0),
                change_pct=stock.get("regularMarketChangePercent", 0.0),
                high=stock.get("dayHigh", 0.0),
                low=stock.get("dayLow", 0.0),
                volume=stock.get("volume", 0),
            ))
        return results

    @staticmethod
    def add_ticker_to_watchlist(ticker: str):
        return WatchlistRepository.add_ticker(ticker.upper())

    @staticmethod
    def remove_ticker_from_watchlist(ticker: str):
        return WatchlistRepository.delete_ticker(ticker.upper())