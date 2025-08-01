from datetime import date, timedelta, datetime
from typing import List, Dict, Any
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
  
async def portfolio_calc() -> List[Dict[str, Any]]:
    response = client.table("transactions").select("*").execute()
    if not response.data:
        return []

    df = pd.DataFrame(response.data)

    total_qty = df.groupby(['ticker', 'name'])['quantity'].sum().reset_index(name="quantity")

    buys = df[df['quantity'] > 0].copy()
    buys['weighted_price'] = buys['price'] * buys['quantity']

    avg_price = (
        buys.groupby(['ticker', 'name'])
        .agg(total_bought_qty=('quantity', 'sum'), total_weighted_price=('weighted_price', 'sum'))
        .reset_index()
    )
    avg_price['avg_price'] = avg_price['total_weighted_price'] / avg_price['total_bought_qty'].round(2)

    processed = pd.merge(total_qty, avg_price[['ticker', 'avg_price']], on=['ticker'], how='left')
    
    # Fetch live prices in batch
    tickers = processed['ticker'].tolist()
    live_prices = await fetch_live_prices(TickersRequest(tickers=tickers))
    price_map = {p.ticker: p.price for p in live_prices if p.price is not None}

    # Map live prices back to DataFrame
    processed['live_price'] = processed['ticker'].map(price_map)
    
    #processed['live_price'] = processed['ticker'].apply(lambda x: fetch_live_price(x) if x else 0)
    processed['price_delta'] = processed['live_price'] - processed['avg_price']
    processed['pct_delta'] = processed['price_delta'] / processed['avg_price']
    processed['pnl'] = processed['price_delta'] * processed['quantity']

    return processed.to_dict(orient='records')
