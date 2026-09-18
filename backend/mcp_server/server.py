import os
import sys
import logging
from typing import List, Dict, Any, Optional
from mcp.server.mcpserver import MCPServer

# Ensure we can import backend packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.scrapers.amazon import check_amazon_price as scrape_amazon
from backend.scrapers.ubuy import check_ubuy_stock as scrape_ubuy
from backend.scrapers.types import ScrapeError
from backend.db.session import SessionLocal
from backend.db.models import Product, PriceHistory, StockHistory

logger = logging.getLogger(__name__)

# Create the MCP server instance
mcp = MCPServer("inventory-intel-agent")

@mcp.tool()
def check_amazon_price(asin: str) -> dict:
    """
    Scrapes the live Amazon product page for the given ASIN.
    Returns the parsed title, price, currency, and stock status.
    If parsing fails or rate limits are hit, returns a structured error dictionary.
    """
    try:
        res = scrape_amazon(asin)
        return {
            "status": "success",
            "title": res.title,
            "price": res.price,
            "currency": res.currency,
            "in_stock": res.in_stock,
            "checked_at": res.checked_at.isoformat()
        }
    except ScrapeError as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "UnknownError",
            "message": str(e)
        }

@mcp.tool()
def check_ubuy_stock(product_url: str, region: str) -> dict:
    """
    Scrapes the live Ubuy product page for the given URL and region.
    Returns the parsed title, price (if visible), currency, and stock status.
    If parsing fails or rate limits are hit, returns a structured error dictionary.
    """
    try:
        res = scrape_ubuy(product_url, region)
        return {
            "status": "success",
            "title": res.title,
            "price": res.price,
            "currency": res.currency,
            "in_stock": res.in_stock,
            "checked_at": res.checked_at.isoformat()
        }
    except ScrapeError as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": "UnknownError",
            "message": str(e)
        }

@mcp.tool()
def list_watchlist(active_only: bool = True) -> list[dict]:
    """
    Retrieves the list of products from the database that are currently being monitored.
    If active_only is True, returns only products marked as active.
    """
    db = SessionLocal()
    try:
        query = db.query(Product)
        if active_only:
            query = query.filter(Product.active == True)
        products = query.all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "source": p.source.value if p.source else None,
                "external_id": p.external_id,
                "region": p.region,
                "currency": p.currency,
                "price_drop_threshold_pct": p.price_drop_threshold_pct,
                "notify_on_restock": p.notify_on_restock,
                "active": p.active
            }
            for p in products
        ]
    finally:
        db.close()

@mcp.tool()
def get_price_history(product_id: int, limit: int = 10) -> list[dict]:
    """
    Retrieves the most recent price history records for a given product ID from the database.
    """
    db = SessionLocal()
    try:
        history = db.query(PriceHistory).filter(PriceHistory.product_id == product_id)\
            .order_by(PriceHistory.checked_at.desc()).limit(limit).all()
        return [
            {
                "id": h.id,
                "product_id": h.product_id,
                "price": h.price,
                "currency": h.currency,
                "checked_at": h.checked_at.isoformat()
            }
            for h in history
        ]
    finally:
        db.close()

@mcp.tool()
def get_stock_history(product_id: int, limit: int = 10) -> list[dict]:
    """
    Retrieves the most recent stock history records for a given product ID from the database.
    """
    db = SessionLocal()
    try:
        history = db.query(StockHistory).filter(StockHistory.product_id == product_id)\
            .order_by(StockHistory.checked_at.desc()).limit(limit).all()
        return [
            {
                "id": h.id,
                "product_id": h.product_id,
                "in_stock": h.in_stock,
                "checked_at": h.checked_at.isoformat()
            }
            for h in history
        ]
    finally:
        db.close()

@mcp.tool()
def record_price_check(product_id: int, price: float, currency: str) -> dict:
    """
    Inserts a new price history record for a given product ID into the database.
    Use this to persist the results of a successful price scrape.
    """
    db = SessionLocal()
    try:
        record = PriceHistory(product_id=product_id, price=price, currency=currency)
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "status": "success",
            "id": record.id,
            "product_id": record.product_id,
            "price": record.price,
            "currency": record.currency,
            "checked_at": record.checked_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@mcp.tool()
def record_stock_check(product_id: int, in_stock: bool) -> dict:
    """
    Inserts a new stock history record for a given product ID into the database.
    Use this to persist the results of a successful stock scrape.
    """
    db = SessionLocal()
    try:
        record = StockHistory(product_id=product_id, in_stock=in_stock)
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "status": "success",
            "id": record.id,
            "product_id": record.product_id,
            "in_stock": record.in_stock,
            "checked_at": record.checked_at.isoformat()
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
