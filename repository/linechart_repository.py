from typing import List, Dict, Any
from datetime import date

from repository.database import create_supabase_client

class LinechartRepository:

    @staticmethod
    def get_linechart_data() -> List[Dict[str, Any]]:
        client = create_supabase_client()

        page_size = 1000
        all_data = []
        offset = 0

        while True:
            response = (
                client.table("portfolio_linechart")
                .select("*")
                .order("date", desc=False)
                .range(offset, offset + page_size - 1)
                .execute()
            )

            if not response.data:
                break

            all_data.extend(response.data)

            # If fewer than page_size rows returned, we can stop fetching
            if len(response.data) < page_size:
                break

            offset += page_size

        return all_data
    
    @staticmethod
    def upsert_linechart_data(row: Dict[str, Any]) -> int:
        client = create_supabase_client()
        try:
            response = client.table("portfolio_linechart") \
                .upsert(row, count="exact") \
                .execute()
        except Exception as e:
            raise Exception(f"Failed to upsert linechart data row: {str(e)}")

        return response.count if response.count else 0
    
    @staticmethod
    def delete_data_older_than_date(keep_from_date: date) -> int:
        client = create_supabase_client()
        try:
            response = client.table("portfolio_linechart") \
            .delete(count="exact") \
            .lt("date", keep_from_date.isoformat()) \
            .execute()
        except Exception as e:
            raise Exception(f"Failed to delete old linechart data: {str(e)}")
        
        return response.count if response.count else 0