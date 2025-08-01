from typing import List, Dict, Any
import pandas as pd

from models import TickersRequest
from repository.transaction_repository import TransactionRepository
from crud import fetch_live_prices

class PortfolioService:
    @staticmethod
    async def portfolio_calc() -> List[Dict[str, Any]]:
        transactions = TransactionRepository.get_all_transactions()
        transactions = [t.model_dump() for t in transactions]
        
        df = pd.DataFrame(transactions)

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
        processed = processed.dropna(subset=['live_price'])
        
        #processed['live_price'] = processed['ticker'].apply(lambda x: fetch_live_price(x) if x else 0)
        processed['price_delta'] = processed['live_price'] - processed['avg_price']
        processed['pct_delta'] = processed['price_delta'] / processed['avg_price']
        processed['pnl'] = processed['price_delta'] * processed['quantity']
        processed['id'] = processed.index.astype(str)

        return processed.to_dict(orient='records')
