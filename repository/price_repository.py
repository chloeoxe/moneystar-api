from typing import List

from repository.database import create_supabase_client
from model.price_model import TickerPrice

class PriceRepository:

    @staticmethod
    def get_all_prices() -> List[TickerPrice]:
        client = create_supabase_client()
        response = client.table("prices").select("*").execute()
        if not response.data:
            return []
        return [TickerPrice(**price) for price in response.data]