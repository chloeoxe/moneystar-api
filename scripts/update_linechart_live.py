import asyncio
from datetime import datetime
from service.chart_service import ChartService

async def main():
    try:
        result = await ChartService.compute_and_store_live_linechart_value()

        print("===== Linechart live data successfully updated =====")
        print(f"{datetime.now()}")
        print(f"Upsert count: {result['upsert_count']}")
        print(f"Upsert value: {result['upsert_value']}")
    
    except Exception as e:
        print(f"Error updating live linechart data: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())