import pytest
from supabase import Client, create_client
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def anyio_backend():
    return "asyncio"

# @pytest.fixture(scope="function")
# def clean_table_client(monkeypatch):
#     proj_url = os.environ.get("TEST_PROJECT_URL")
#     api_key = os.environ.get("TEST_API_KEY")
#     client = create_client(proj_url, api_key)
#     client.table("transactions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
#     monkeypatch.setattr("repository.transaction_repository.create_supabase_client", lambda: client)
#     yield client
#     client.table("transactions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
