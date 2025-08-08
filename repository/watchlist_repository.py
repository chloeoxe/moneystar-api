from repository.database import create_supabase_client

class WatchlistRepository:

    @staticmethod
    def get_all_tickers():
        client = create_supabase_client()
        res = client.table("watchlist").select("ticker").execute()
        if not res.data:
            return []
        return [r["ticker"] for r in res.data]

    @staticmethod
    def add_ticker(ticker: str):
        client = create_supabase_client()
        existing = client.table("watchlist").select("*").eq("ticker", ticker).execute()
        if existing.data:
            return  # already exists
        res = client.table("watchlist").insert({"ticker": ticker}, count="exact").execute()
        return res.count if res.count else 0

    @staticmethod
    def delete_ticker(ticker: str):
        client = create_supabase_client()
        res = client.table("watchlist").delete(count="exact").eq("ticker", ticker).execute()
        return res.count if res.count else 0