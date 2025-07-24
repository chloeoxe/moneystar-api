from fastapi import FastAPI
from database import create_supabase_client

app = FastAPI()

supabase = create_supabase_client()

@app.get("/")
async def root():
    return {"message": "Hello, this is MoneyStar's API!"}

@app.get("/transactions")
async def get_transactions():
    response = (
        supabase.table("transactions")
        .select("*", count="exact")
        .execute()
    )
    return response