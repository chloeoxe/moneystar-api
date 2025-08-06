from datetime import date, timedelta
import pandas as pd
from typing import List, Dict, Any

from repository.transaction_repository import TransactionRepository
from repository.price_repository import PriceRepository
from service.price_service import PriceService
from model.price_model import TickersLivePriceRequest

class ChartService:
    """Service class to handle chart-related operations."""

    @staticmethod
    def get_portfolio_linechart_data() -> List[Dict[str, Any]]:
        transactions = TransactionRepository.get_all_transactions()
        if not transactions:
            return []

        # Convert transactions to DataFrame
        df_txn = pd.DataFrame([t.model_dump() for t in transactions])
        df_txn["transaction_date"] = pd.to_datetime(df_txn["transaction_date"])

        # Extract all tickers used
        tickers = df_txn["ticker"].unique().tolist()

        # Get present date
        end_date = date.today()

        # Fetch only relevant price data once
        all_prices = PriceRepository.get_prices_for_tickers_before(tickers, end_date)
        df_prices = pd.DataFrame(all_prices)
        df_prices["date"] = pd.to_datetime(df_prices["date"])

        # Determine date range
        start_date = df_prices["date"].min().date()
        all_dates = pd.date_range(start=start_date, end=end_date, freq="D")

        chart_data = []

        for d in all_dates:
            # Get all transactions up to date d
            df_txn_until_d = df_txn[df_txn["transaction_date"] <= d]

            # Aggregate holdings as of date d
            holdings = df_txn_until_d.groupby("ticker")["quantity"].sum()
            holdings = holdings[holdings > 0]

            total_value = 0.0

            for ticker, qty in holdings.items():
                # Filter prices for this ticker up to d
                prices = df_prices[(df_prices["ticker"] == ticker) & (df_prices["date"] <= d)]
                
                if not prices.empty:
                    latest_price = prices.sort_values("date", ascending=False).iloc[0]["close"]
                    total_value += qty * latest_price

            chart_data.append({
                "date": d.date().isoformat(),
                "value": round(total_value, 2)
            })

        return chart_data

    @staticmethod
    async def get_all_portfolio_prices_and_values() -> pd.DataFrame:
        """Obtains the current portfolio live prices and values (quantity * prices) for each ticker.

        Returns:
            pd.DataFrame: Returns a DataFrame with tickers, quantities, live prices, and values (quantity * prices) of the portfolio.
        """
        transactions = TransactionRepository.get_all_transactions()
        if not transactions:
            return pd.DataFrame(columns=["ticker", "quantity", "price", "value"])
        
        transactions = [t.model_dump() for t in transactions]
        transactions = pd.DataFrame(transactions)

        # Calculate total quantity for each ticker
        ticker_quantities = transactions.groupby("ticker")["quantity"].sum()
        ticker_quantities = ticker_quantities[ticker_quantities > 0]
        
        # Fetch live prices for each ticker
        tickers = ticker_quantities.index.tolist()
        prices = await PriceService.fetch_live_prices(TickersLivePriceRequest(tickers=tickers))
        price_data = pd.DataFrame([{"ticker": p.ticker, "price": p.close} for p in prices])
        price_data.set_index("ticker", inplace=True)

        # Calculate total value held for each ticker
        df = pd.DataFrame(ticker_quantities).join(price_data)
        df.dropna(subset=["price"], inplace=True) 
        df["value"] = df["quantity"] * df["price"]
        
        return df.reset_index()
    
    @staticmethod
    async def get_portfolio_distribution_data() -> List[Dict[str, Any]]:
        """Obtains the current portfolio distribution data for top 5 holdings and collapses the others into a 'Others' category.

        Returns:
            List[Dict[str, Any]]: Returns a list of dictionaries with ticker and value for top 5 holdings and 'Others'.
        """
        df = await ChartService.get_all_portfolio_prices_and_values()
        if df.empty:
            return []
        
        df = df.sort_values(by="value", ascending=False).reset_index()

        # Segregate top 5 holdings
        top_df = df.head(5)[["ticker", "value"]]

        # Sum of remaining holdings into 'Others'
        if len(df) > 5:
            others_value = df.iloc[5:]["value"].sum()
            others_row = pd.DataFrame([{"ticker": "Others", "value": others_value}])
            result_df = pd.concat([top_df, others_row], ignore_index=True)
        else:
            result_df = top_df

        return result_df.to_dict(orient="records")
    
    @staticmethod
    async def get_all_portfolio_prices_and_values_including_last_month() -> pd.DataFrame:
        """Obtains the current portfolio live prices and values (quantity * prices) for each ticker, along with last month's prices.

        Returns:
            pd.DataFrame: Returns a DataFrame with tickers, quantities, live prices, and values (quantity * prices) of the portfolio and last month's prices and value.
        """
        df = await ChartService.get_all_portfolio_prices_and_values()
        if df.empty:
            return pd.DataFrame(columns=["ticker", "quantity", "price", "value", "prev_price"])
        
        today = pd.Timestamp.today().normalize()
        close_window = today - pd.DateOffset(months=1)
        start_window = close_window - pd.DateOffset(days=5) # buffer for market closing
        close_window = str(close_window)[:10]
        start_window = str(start_window)[:10]
        
        # TODO: Compute historical quantities of each ticker at a specific point in time. 
        
        # TODO: Migrate to fetch from historical prices table
        # Currently fetching hisotrical prices directly from yfinance
        from live_prices import fetch_historical_prices
        df["prev_price"] = df["ticker"].astype(object).apply(lambda x: round(float(fetch_historical_prices(x, start_window, close_window)[0] if x else 0), 2))
        return df
    
    @staticmethod
    async def get_top_holdings_performance_data() -> List[Dict[str, Any]]:
        """Obtains the top 5 holdings performance data, including their current value, previous value, fixed change, and percentage change.

        Returns:
            List[Dict[str, Any]]: Returns a list of dictionaries with ticker, value, previous value, fixed change, and percentage change for the top 5 holdings.
        """
        df = await ChartService.get_all_portfolio_prices_and_values_including_last_month()
        if df.empty:
            return []
        
        # Calculate fixed change and percentage change
        df = df.sort_values(by="value", ascending=False).head(5).reset_index()
        df["fixed_change"] = round(df["price"] - df["prev_price"], 2)
        df["percentage_change"] = round(df["fixed_change"] / df["prev_price"].replace(0, 1) * 100, 2)
        df = df.drop('value', axis=1)
        
        df = df.rename(columns={'price': 'value', 'prev_price': 'prev_value'})
        return df[["ticker", "value", "prev_value", "fixed_change", "percentage_change"]].to_dict(orient="records")
    
    @staticmethod
    async def get_overall_portfolio_month_change() -> Dict[str, float]:
        """Obtains the overall portfolio month change, including the current value and previous value.

        Returns:
            Dict[str, float]: Returns a dictionary with the current value and previous value of the overall portfolio.
        """
        df = await ChartService.get_all_portfolio_prices_and_values_including_last_month()
        if df.empty:
            return {"value": 0.0, "prev_value": 0.0}
        
        # Compute the previous value based on the previous month's price and current quantity
        df["prev_value"] = df["prev_price"] * df["quantity"]
        totals = df.sum()
        return {"value": float(totals["value"]), "prev_value": float(totals["prev_value"])}