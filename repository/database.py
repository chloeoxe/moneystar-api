from supabase import Client, create_client
import os
from dotenv import load_dotenv

load_dotenv()

proj_url = os.environ.get("PROJECT_URL")
api_key = os.environ.get("API_KEY")

def create_supabase_client():
    supabase: Client = create_client(proj_url, api_key)
    return supabase