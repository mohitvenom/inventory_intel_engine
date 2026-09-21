import asyncio
from tests.evals.test_summary_evals import run_summary_async
import json

traces = {
    "all_success": [
        {"id": 1, "name": "Apple iPad", "status": "success", "price": 400.0, "in_stock": True, "price_dropped": False, "restocked": False, "stockouted": False},
        {"id": 2, "name": "Xbox Gift Card", "status": "success", "price": 50.0, "in_stock": True, "price_dropped": False, "restocked": False, "stockouted": False}
    ],
    "all_error": [
        {"id": 1, "name": "EVGA RTX 3090", "status": "error", "error": "RegionRestrictedError"},
    ],
    "price_drop": [
        {"id": 1, "name": "Apple iPad", "status": "success", "price": 300.0, "in_stock": True, "price_dropped": True, "restocked": False, "stockouted": False},
    ],
    "restock": [
        {"id": 1, "name": "The 48 Laws of Power", "status": "success", "price": 20.0, "in_stock": True, "price_dropped": False, "restocked": True, "stockouted": False},
    ]
}

async def main():
    for name, trace in traces.items():
        print(f"=== {name} ===")
        res = await run_summary_async(trace)
        print(res)

if __name__ == "__main__":
    asyncio.run(main())
