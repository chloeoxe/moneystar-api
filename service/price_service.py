import yfinance as yf
import pandas as pd
from typing import List
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import pandas_market_calendars as mcal

from repository.price_repository import PriceRepository
from repository.transaction_repository import TransactionRepository
from model.price_model import TickersLivePriceRequest, TickerPrice, PriceUpdateRequest, PriceUpdateResponse, TickerPriceUpdateRequest, TickerPriceUpdateResponse

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
    
    @staticmethod
    async def get_market_open_dates(start_date: date, end_date: date):
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(start_date=start_date, end_date=end_date)
        return schedule.index.date.tolist()
        
    @staticmethod
    async def fetch_missing_prices(ticker: str, missing_dates: List[date]) -> List[TickerPrice]:
        if not missing_dates:
            return []

        start_date = min(missing_dates)
        end_date = max(missing_dates)
        df = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1), progress=False, auto_adjust=True)
        if df.empty:
            return []

        results = []

        if 'Close' not in df.columns:
            print(f"No 'Close' column in dataframe for ticker {ticker}")
            return results

        close_series = df["Close"]
        close_series.index = close_series.index.date
        date_price_map = dict(zip(close_series.index, close_series.values))

        for dt in missing_dates:
            close_price = date_price_map.get(dt)
            if pd.notna(close_price):
                results.append(TickerPrice(
                    ticker=ticker,
                    date=dt,
                    close=float(close_price)
                ))
            else:
                print(f"No price found for {ticker} on {dt}")

        return results
        
    @staticmethod
    async def update_prices_for_ticker(request: TickerPriceUpdateRequest) -> TickerPriceUpdateResponse:
        ticker = request.ticker
        earliest_buy_date = request.earliest_buy_date
        years_to_keep = request.years_to_keep
        months_before_earliest = request.months_before_earliest

        # Calculate the date range to keep prices
        today = date.today()
        keep_from_date = today - relativedelta(years=years_to_keep)

        adjusted_start = earliest_buy_date - relativedelta(months=months_before_earliest)
        start_date = max(adjusted_start, keep_from_date)

        # Get market open dates between start_date and today
        required_dates = await PriceService.get_market_open_dates(start_date, today)

        # Get existing dates for the ticker and compute missing dates
        existing_dates = PriceRepository.get_existing_dates_per_ticker(ticker, start_date)
        missing_dates = list(set(required_dates) - set(existing_dates))

        # Fetch missing prices and insert into prices table
        new_prices = await PriceService.fetch_missing_prices(ticker, missing_dates)
        if new_prices:
            insert_count = PriceRepository.upsert_prices(new_prices)

        return TickerPriceUpdateResponse(
            ticker=ticker,
            missing_dates_fetched=len(new_prices)
        )
    
    @staticmethod
    async def update_prices(request: PriceUpdateRequest) -> PriceUpdateResponse:
        years_to_keep = request.years_to_keep
        months_before_earliest = request.months_before_earliest

        today = date.today()
        keep_from_date = today - relativedelta(years=years_to_keep)

        # Get all buy transactions
        transactions = TransactionRepository.get_buy_transactions()

        if not transactions:
            return PriceUpdateResponse(
                tickers_updated=[],
                total_new_prices_added=0,
                total_old_prices_deleted=0,
                update_details={}
            )

        # Use pandas to group by ticker and get earliest transaction_date
        df = pd.DataFrame(transactions)
        df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date
        grouped = df.groupby("ticker")["transaction_date"].min().to_dict()

        total_new = 0
        update_dict = {}

        for ticker, earliest_buy_date in grouped.items():
            res = await PriceService.update_prices_for_ticker(
                TickerPriceUpdateRequest(
                    ticker=ticker,
                    earliest_buy_date=earliest_buy_date,
                    years_to_keep=years_to_keep,
                    months_before_earliest=months_before_earliest
                )
            )
            total_new += res.missing_dates_fetched
            update_dict[ticker] = res.missing_dates_fetched

        # Delete old prices
        delete_count = PriceRepository.delete_prices_older_than_date(keep_from_date)

        return PriceUpdateResponse(
            tickers_updated=list(grouped.keys()),
            total_new_prices_added=total_new,
            total_old_prices_deleted=delete_count,
            update_details=update_dict
        )