import asyncio
from datetime import datetime
from service.price_service import PriceService
from model.price_model import PriceUpdateRequest

async def main():
    request = PriceUpdateRequest(
        years_to_keep=5,
        months_before_earliest=2
    )

    try:
        result = await PriceService.update_prices(request)

        print("===== Prices table successfully updated =====")
        print(f"{datetime.now()}")
        print(f"Tickers updated: {result.tickers_updated}")
        print(f"New prices added: {result.total_new_prices_added}")
        print(f"Old prices deleted: {result.total_old_prices_deleted}")
        print(f"Update details: {result.update_details}")
    
    except Exception as e:
        print(f"Error updating prices table: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())