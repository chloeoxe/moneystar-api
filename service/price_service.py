import yfinance as yf
import pandas as pd
from typing import List
from datetime import date, timedelta, datetime

from repository.price_repository import PriceRepository
from model.price_model import TickersLivePriceRequest, TickerPrice

class PriceService: 
    
    @staticmethod
    def get_historical_prices() -> List[TickerPrice]:
        """
        Fetch all historical prices from the prices table
        """
        return PriceRepository.get_all_prices()
    
    @staticmethod
    async def fetch_live_prices(request: TickersLivePriceRequest) -> List[TickerPrice]:
        target_date = date.today() if request.target_date is None else datetime.strptime(request.target_date, '%Y-%m-%d').date()
        start_date = target_date - timedelta(days=5)
        end_date = target_date + timedelta(days=1)

        try:
            data = yf.download(
                tickers=request.tickers,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=request.interval,
                progress=False,
                threads=True,
                auto_adjust=True
            )

            results = []

            if isinstance(data.columns, pd.MultiIndex):
                # Add latest closing price for each ticker into results
                for ticker in request.tickers:
                    try:
                        price_series = data[("Close", ticker)]
                        price = price_series.dropna().iloc[-1] if not price_series.dropna().empty else None
                        latest_date = price_series.index[-1].date() if not price_series.dropna().empty else None
                        results.append(TickerPrice(ticker=ticker, date=latest_date, close=round(price, 2) if price else None))
                    except Exception as e:
                        results.append(TickerPrice(ticker=ticker, date=None, close=None))

            return results

        except Exception as e:
            # Raise exception if entire batch request fails
            raise Exception(f"[yfinance] Live prices batch request failed: {str(e)}")