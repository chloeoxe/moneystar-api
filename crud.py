import random
from datetime import date
from typing import List, Dict, Any
from model.transaction_model import TransactionCreate, TransactionUpdate
from repository.database import create_supabase_client
from repository.transaction_repository import TransactionRepository
import pandas as pd

from service.price_service import PriceService

client = create_supabase_client()

def transactions_read() -> List[Dict[str, Any]]:
    return TransactionRepository.get_all_transactions()

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

def get_historical_prices() -> List[Dict[str, Any]]:
    response = client.table("prices").select("*").execute()
    if not response.data:
        return []
    return response.data

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
    live_prices = await PriceService.fetch_live_prices(tickers)
    price_map = {p.ticker: p.price for p in live_prices if p.price is not None}

    # Map live prices back to DataFrame
    processed['live_price'] = processed['ticker'].map(price_map)
    
    #processed['live_price'] = processed['ticker'].apply(lambda x: fetch_live_price(x) if x else 0)
    processed['price_delta'] = processed['live_price'] - processed['avg_price']
    processed['pct_delta'] = processed['price_delta'] / processed['avg_price']
    processed['pnl'] = processed['price_delta'] * processed['quantity']

    return processed.to_dict(orient='records')
