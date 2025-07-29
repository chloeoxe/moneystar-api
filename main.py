from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_supabase_client

app = FastAPI()

supabase = create_supabase_client()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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