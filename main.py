from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller import chart_routes, transaction_routes, portfolio_routes, price_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chart_routes.router)
app.include_router(transaction_routes.router)
app.include_router(portfolio_routes.router)
app.include_router(price_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to MoneyStar's API!"}
