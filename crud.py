from datetime import date, timedelta
from typing import List, Dict, Any
from models import TransactionCreate, TransactionUpdate
from database import create_supabase_client
from live_prices import fetch_live_price, fetch_historical_prices
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

def get_portfolio_distribution_data() -> List[Dict[str, Any]]:
    response = client.table("transactions").select("*").execute()
    if not response.data:
        return []
    
    transactions = response.data
    
    total_ticker_quantities = {}
    for transaction in transactions:
        total_ticker_quantities[transaction["ticker"]] = total_ticker_quantities.get(transaction["ticker"], 0) + transaction["quantity"]
     
    total_ticker_quantities = {k: v for k, v in total_ticker_quantities.items() if v > 0}
    
    total_ticker_price = {}
    for ticker, quantity in total_ticker_quantities.items():
        try:
            price = fetch_live_price(ticker)
            total_ticker_price[ticker] = round(price * quantity, 2)
        except ValueError as e:
            raise ValueError(f"Error fetching price for {ticker}: {e}")
    
    chart_data = [{"ticker": ticker, "value": value} for ticker, value in total_ticker_price.items()]
    df = pd.DataFrame(chart_data)
    chart_data = df.sort_values(by='value', ascending=False).head(5).to_dict(orient='records')
    
    return chart_data

def get_top_holdings_performance_data() -> List[Dict[str, Any]]:
    # Obtains the top 5 holdings computed in the get_portfolio_distribution_data function
    total_ticker_price = get_portfolio_distribution_data()
    if not total_ticker_price:
        return []   
    
    today = pd.Timestamp.today().normalize()
    close_window = today - pd.DateOffset(months=1)
    start_window = close_window - pd.DateOffset(days=5) # buffer for market closing
    close_window = str(close_window)[:10]
    start_window = str(start_window)[:10]
    
    # Fetch live prices and historical prices for the top holdings
    for item in total_ticker_price:
        value = round(fetch_live_price(item['ticker']), 2)
        prev_value = round(fetch_historical_prices(item['ticker'], start_window, close_window)[0], 2)
        item['prev_value'] = prev_value
        item['value'] = value
    
    return total_ticker_price