from datetime import date, timedelta, datetime
from typing import List, Dict, Any

import numpy as np
from model.transaction_model import TransactionCreate, TransactionUpdate
from repository.database import create_supabase_client
from repository.transaction_repository import TransactionRepository
from models import TickersRequest, TickerPrice
from repository.database import create_supabase_client
import yfinance as yf
import pandas as pd

client = create_supabase_client()
    
def get_historical_prices() -> List[Dict[str, Any]]:
    response = client.table("prices").select("*").execute()
    if not response.data:
        return []
    return response.data

async def fetch_live_prices(request: TickersRequest) -> list[TickerPrice]:
    target_date = date.today() if request.target_date is None else datetime.strptime(request.target_date, '%Y-%m-%d').date()
    start_date = target_date - timedelta(days=3)
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
                    results.append(TickerPrice(ticker=ticker, date=latest_date, price=round(price, 2) if price else None))
                except Exception as e:
                    results.append(TickerPrice(ticker=ticker, date=None, price=None))

        return results

    except Exception as e:
        # Raise exception if entire batch request fails
        raise Exception(f"[yfinance] Live prices batch request failed: {str(e)}")
  