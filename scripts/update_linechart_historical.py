import asyncio
from datetime import datetime
from service.chart_service import ChartService

async def main():
    try:
        result = await ChartService.compute_and_store_historical_linechart_values()

        print("===== Linechart historical data successfully updated =====")
        print(f"{datetime.now()}")
        print(f"Start date: {result['start_date']}")
        print(f"End date: {result['end_date']}")
        print(f"Upsert count: {result['upsert_count']}")
        print(f"Delete count: {result['delete_count']}")
    
    except Exception as e:
        print(f"Error updating historical linechart data: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())