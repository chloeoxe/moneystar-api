from typing import List, Dict, Any

from repository.database import create_supabase_client

class TransactionRepository:
    
    @staticmethod
    def get_all_transactions() -> List[Dict[str, Any]]:
        client = create_supabase_client()
        response = client.table("transactions").select("*").execute()
        if not response.data:
            return []
        return response.data
