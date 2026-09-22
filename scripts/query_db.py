"""
A general DB inspection utility to check product details and test manual price checks.
"""
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.db.session import SessionLocal
from backend.db.models import Product, PriceHistory, StockHistory
from backend.app.api import invoke_mcp_tool_with_timeout

async def test():
    db = SessionLocal()
    try:
        amazon_prods = db.query(Product).filter(Product.source == "amazon").all()
        for p in amazon_prods:
            print(f"Product: {p.id} | {p.name} | {p.external_id} | {p.source}")
            # check if there's any price/stock history
            ph = db.query(PriceHistory).filter(PriceHistory.product_id == p.id).all()
            sh = db.query(StockHistory).filter(StockHistory.product_id == p.id).all()
            print(f"Price History count: {len(ph)}, Stock History count: {len(sh)}")
            print("---")
            
            print(f"Testing manual check for external_id: {p.external_id}")
            res = await invoke_mcp_tool_with_timeout("check_amazon_price", {"asin": p.external_id})
            print(f"Check result: {res}")
            print("=================")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test())
