from typing import List, Dict, Any, Optional
import pandas as pd

from repository.transaction_repository import TransactionRepository
from service.price_service import PriceService
from model.price_model import TickersLivePriceRequest

class PortfolioService:
    @staticmethod
    async def portfolio_summary() -> List[Dict[str, Any]]:
        curr_date = pd.to_datetime("today").normalize()
        one_month_ago = curr_date - pd.DateOffset(months=1)

        pf = await PortfolioService.portfolio_calc(json=False)
        pf_last_month = await PortfolioService.portfolio_calc(date=one_month_ago.strftime('%Y-%m-%d'), json=False)

        total_value = (pf['live_price'] * pf['quantity']).sum()
        total_value_last_month = (pf_last_month['live_price'] * pf_last_month['quantity']).sum()
        monthly_pnl = total_value - total_value_last_month
        monthly_pnl_pct = (monthly_pnl / total_value_last_month * 100) if total_value_last_month else 0
        all_time_returns = pf['pnl'].sum()
        all_time_returns_pct = (all_time_returns / total_value * 100) if total_value else 0
        cash = 0  # Assuming cash is not tracked in this context
        cash_pct = 0  # Assuming cash percentage is not tracked

        summary = {
            "total_value": total_value,
            "total_value_pct": (total_value - total_value_last_month) / total_value_last_month * 100 if total_value_last_month else 0,
            "monthly_pnl": monthly_pnl,
            "monthly_pnl_pct": monthly_pnl_pct,
            "all_time_returns": all_time_returns,
            "all_time_returns_pct": all_time_returns_pct,
            "cash": cash,
            "cash_pct": cash_pct
        }

        return summary

    @staticmethod
    async def portfolio_calc(date: Optional[str] = None, json: bool = True) -> List[Dict[str, Any]]:
        transactions = TransactionRepository.get_all_transactions()
        transactions = [t.model_dump() for t in transactions]
        
        df = pd.DataFrame(transactions)

        if date:
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            df = df[df['transaction_date'] <= pd.to_datetime(date)]

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
        live_prices = await PriceService.fetch_live_prices(TickersLivePriceRequest(tickers=tickers, target_date=date))
        price_map = {p.ticker: p.close for p in live_prices if p.close is not None}

        # Map live prices back to DataFrame
        processed['live_price'] = processed['ticker'].map(price_map)
        processed = processed.dropna(subset=['live_price'])
        
        processed['price_delta'] = processed['live_price'] - processed['avg_price']
        processed['pct_delta'] = processed['price_delta'] / processed['avg_price'] * 100
        processed['pnl'] = processed['price_delta'] * processed['quantity']
        processed['id'] = processed.index.astype(str)

        return processed.to_dict(orient='records') if json else processed
