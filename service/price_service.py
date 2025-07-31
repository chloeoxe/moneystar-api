import yfinance as yf
import pandas as pd

from model.ticker_model import TickerPrice

class PriceService: 
    @staticmethod
    async def fetch_live_prices(tickers: list[str]) -> list[TickerPrice]:
        try:
            data = yf.download(
                tickers=tickers,
                period="1d",
                interval="1m",
                progress=False,
                threads=True,
                auto_adjust=True
            )

            results = []

            if isinstance(data.columns, pd.MultiIndex):
                # Add latest closing price for each ticker into results
                for ticker in tickers:
                    try:
                        price_series = data[("Close", ticker)]
                        price = price_series.dropna().iloc[-1] if not price_series.dropna().empty else None
                        results.append(TickerPrice(ticker=ticker, price=round(price, 2) if price else None))
                    except Exception as e:
                        results.append(TickerPrice(ticker=ticker, price=None))

            return results

        except Exception as e:
            # Raise exception if entire batch request fails
            raise Exception(f"[yfinance] Live prices batch request failed: {str(e)}")
