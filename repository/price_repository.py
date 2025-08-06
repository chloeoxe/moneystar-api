from typing import List, Dict, Any
from datetime import date

from repository.database import create_supabase_client
from model.price_model import TickerPrice

class PriceRepository:

    @staticmethod
    def get_all_prices() -> List[TickerPrice]:
        client = create_supabase_client()

        page_size = 1000
        start = 0
        existing_prices = []

        while True:
            response = client.table("prices").select("*").execute()

            if not response.data:
                break
            
            page_prices = [TickerPrice(**price) for price in response.data]
            existing_prices.extend(page_prices)

            # If we got less than a full page, we can stop fetching
            if len(response.data) < page_size:
                break

            start += page_size
        
        return existing_prices
    
    @staticmethod
    def get_existing_dates_per_ticker(ticker: str, start_date: date) -> List[date]:
        client = create_supabase_client()

        page_size = 1000
        start = 0
        existing_dates = []

        while True:
            response = client.table("prices") \
                .select("date") \
                .eq("ticker", ticker) \
                .gte("date", start_date.isoformat()) \
                .range(start, start + page_size - 1) \
                .execute()

            if not response.data:
                break

            page_dates = [date.fromisoformat(r["date"]) for r in response.data]
            existing_dates.extend(page_dates)

            # If we got less than a full page, we can stop fetching
            if len(response.data) < page_size:
                break

            start += page_size

        return existing_dates
    
    @staticmethod
    def upsert_prices(prices: List[TickerPrice]) -> int:
        client = create_supabase_client()
        try:
            data = [
                {**price.model_dump(), "date": price.date.isoformat()}
                for price in prices
            ]
            response = client.table("prices") \
                .upsert(data, count="exact") \
                .execute()
        except Exception as e:
            raise Exception(f"Failed to upsert prices: {str(e)}")

        return response.count if response.count else 0
    
    @staticmethod
    def delete_prices_older_than_date(keep_from_date: date) -> int:
        client = create_supabase_client()
        try:
            response = client.table("prices") \
                .delete(count="exact") \
                .lt("date", keep_from_date.isoformat()) \
                .execute()
        except Exception as e:
            raise Exception(f"Failed to delete old prices: {str(e)}")
        
        return response.count if response.count else 0
        
    @staticmethod
    def get_prices_for_tickers_before(tickers: List[str], max_date: date) -> List[Dict[str, Any]]:
        client = create_supabase_client()

        all_data = []
        chunk_size = 10
        page_size = 1000

        for i in range(0, len(tickers), chunk_size):
            ticker_chunk = tickers[i:i + chunk_size]
            start = 0
            while True:
                end = start + page_size - 1

                response = client.table("prices") \
                    .select("ticker", "date", "close") \
                    .in_("ticker", ticker_chunk) \
                    .lte("date", max_date.isoformat()) \
                    .order("ticker") \
                    .range(start, end) \
                    .execute()

                page_data = response.data
                if not page_data:
                    break

                all_data.extend(page_data)

                if len(page_data) < page_size:
                    break  # no more pages
                start += page_size

        return all_data