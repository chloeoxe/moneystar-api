import random
from datetime import date, timedelta
from typing import List, Dict, Any
from models import TransactionCreate, TransactionUpdate, TickerPrice
from database import create_supabase_client
import yfinance as yf
import pandas as pd

client = create_supabase_client()

def transactions_read() -> List[Dict[str, Any]]:
    response = client.table("transactions").select("*").execute()
    if not response.data:
        return []
    return response.data

def transaction_create(transaction: TransactionCreate) -> dict[str, Any]:
    try:
        if transaction.quantity == 0:
            raise ValueError("Quantity cannot be 0")
        if transaction.price == 0:
            raise ValueError("Price cannot be 0")
        if transaction.transaction_date is None:
            transaction.transaction_date = date.today()

        res = client.table("transactions").insert({
            "ticker": transaction.ticker,
            "name": transaction.name,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "transaction_date": str(transaction.transaction_date)
        }).execute()

        if not res.data:
            raise ValueError("Failed to create transaction: no data returned")
        return res.data[0]
    except Exception as e:
        raise Exception(f"Error creating transaction: {str(e)}")

def transaction_update(transaction_id: str, transaction: TransactionUpdate) -> dict[str, Any]:
    try:
        if transaction.quantity == 0:
            raise ValueError("Quantity cannot be 0")
        if transaction.price == 0:
            raise ValueError("Price cannot be 0")

        data = {k: v for k, v in transaction.model_dump().items() if v is not None}

        res = client.table("transactions").update(data).eq("id", transaction_id).execute()

        if not res.data:
            raise ValueError("Failed to update transaction: no data returned")
        return res.data[0]

    except Exception as e:
        raise Exception(f"Error updating transaction: {str(e)}")
    
def delete_transaction_by_id(transaction_id: str) -> dict[str, Any]:
    try:
        response = client.table("transactions").delete().eq("id", transaction_id).execute()
        if len(response.data) == 0:
            raise ValueError(f"Transaction with id={transaction_id} not found")
        
        return {"message": f"Transaction with id={transaction_id} deleted successfully"}
    except Exception as e:
        raise Exception(f"Error deleting transaction: {str(e)}")

def get_portfolio_linechart_data() -> List[Dict[str, Any]]:
    # Fetch all transactions
    response = client.table("transactions").select("*").execute()

    transactions = response.data

    if not transactions:
        return []

    # Find the earliest transaction date
    earliest_date = min(date.fromisoformat(t["transaction_date"]) for t in transactions)
    today = date.today()

    # Build list of dates from earliest date to today
    num_days = (today - earliest_date).days + 1
    all_dates = [earliest_date + timedelta(days=i) for i in range(num_days)]

    # For each date, compute total portfolio value
    chart_data = []
    for d in all_dates:
        total_value = sum(
            t["quantity"] * t["price"]
            for t in transactions
            if date.fromisoformat(t["transaction_date"]) <= d
        )
        chart_data.append({
            "date": d.isoformat(),
            "value": total_value
        })

    return chart_data

def get_historical_prices() -> List[Dict[str, Any]]:
    response = client.table("prices").select("*").execute()
    if not response.data:
        return []
    return response.data

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

async def get_all_portfolio_prices_and_values() -> pd.DataFrame:
    """Obtains the current portfolio live prices and values (quantity * prices) for each ticker.

    Returns:
        pd.DataFrame: Returns a DataFrame with tickers, quantities, live prices, and values (quantity * prices) of the portfolio.
    """
    response = client.table("transactions").select("*").execute()
    if not response.data:
        return []
    transactions = pd.DataFrame(response.data)

    # Calculate total quantity for each ticker
    ticker_quantities = transactions.groupby("ticker")["quantity"].sum()
    ticker_quantities = ticker_quantities[ticker_quantities > 0]
    
    # Fetch live prices for each ticker
    tickers = ticker_quantities.index.tolist()
    prices = await fetch_live_prices(tickers)
    price_data = pd.DataFrame([{"ticker": p.ticker, "price": p.price} for p in prices])
    price_data.set_index("ticker", inplace=True)

    # Calculate total value held for each ticker
    df = pd.DataFrame(ticker_quantities).join(price_data)
    df["value"] = df["quantity"] * df["price"]
    
    return df.reset_index()

async def get_portfolio_distribution_data() -> List[Dict[str, Any]]:
    df = await get_all_portfolio_prices_and_values()
    
    # Obtain the top 5 holdings by total value
    df = df.sort_values(by="value", ascending=False).head(5).reset_index()
    return df[["ticker", "value"]].to_dict(orient="records")

async def get_all_portfolio_prices_and_values_including_last_month() -> pd.DataFrame:
    """Obtains the current portfolio live prices and values (quantity * prices) for each ticker, along with last month's prices.

    Returns:
        pd.DataFrame: Returns a DataFrame with tickers, quantities, live prices, and values (quantity * prices) of the portfolio and last month's prices and value.
    """
    df = await get_all_portfolio_prices_and_values()
    
    today = pd.Timestamp.today().normalize()
    close_window = today - pd.DateOffset(months=1)
    start_window = close_window - pd.DateOffset(days=5) # buffer for market closing
    close_window = str(close_window)[:10]
    start_window = str(start_window)[:10]
    
    # TODO: Migrate to fetch from historical prices table
    # Currently fetching hisotrical prices directly from yfinance
    from live_prices import fetch_historical_prices
    df["prev_price"] = df["ticker"].astype(object).apply(lambda x: round(float(fetch_historical_prices(x, start_window, close_window)[0] if x else 0), 2))
    return df

async def get_top_holdings_performance_data() -> List[Dict[str, Any]]:
    df = await get_all_portfolio_prices_and_values_including_last_month()
    
    df = df.sort_values(by="value", ascending=False).head(5).reset_index()
    df["fixed_change"] = round(df["price"] - df["prev_price"], 2)
    df["percentage_change"] = round(df["fixed_change"] / df["prev_price"].replace(0, 1) * 100, 2)
    df = df.drop('value', axis=1)
    
    df = df.rename(columns={'price': 'value', 'prev_price': 'prev_value'})
    return df[["ticker", "value", "prev_value", "fixed_change", "percentage_change"]].to_dict(orient="records")

def portfolio_calc() -> List[Dict[str, Any]]:
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
    
    processed['live_price'] = processed['ticker'].apply(lambda x: fetch_live_price(x) if x else 0)
    processed['price_delta'] = processed['live_price'] - processed['avg_price']
    processed['pct_delta'] = processed['price_delta'] / processed['avg_price']
    processed['pnl'] = processed['price_delta'] * processed['quantity']

    return processed.to_dict(orient='records')

async def get_overall_portfolio_month_change() -> Dict[str, float]:
    df = await get_all_portfolio_prices_and_values_including_last_month()
    
    df["prev_value"] = df["prev_price"] * df["quantity"]
    totals = df.sum()
    
    return {"value": float(totals["value"]), "prev_value": float(totals["prev_value"])}