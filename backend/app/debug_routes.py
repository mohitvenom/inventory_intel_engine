from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback

from backend.scrapers.amazon import check_amazon_price
from backend.scrapers.ubuy import check_ubuy_stock
from backend.scrapers.walmart import check_walmart_price
from backend.scrapers.ebay import check_ebay_price
from backend.scrapers.types import ScrapeError

router = APIRouter(prefix="/debug", tags=["debug"])

class AmazonRequest(BaseModel):
    asin: str
    region: str = "com"

class UbuyRequest(BaseModel):
    url: str
    region: str

class WalmartRequest(BaseModel):
    url: str

class EbayRequest(BaseModel):
    url: str

def handle_scrape_error(e: Exception):
    if isinstance(e, ScrapeError):
        raise HTTPException(
            status_code=400,
            detail={"error_type": type(e).__name__, "message": str(e)}
        )
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "error_type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        )

@router.post("/scrape/amazon")
def debug_scrape_amazon(req: AmazonRequest):
    """
    Test the Amazon scraper in isolation.
    Input format: Amazon ASIN only, e.g. B0BTHSK7P1.
    Optionally provide a region, e.g., "in", "co.uk" (default is "com").
    """
    try:
        return check_amazon_price(req.asin, req.region)
    except Exception as e:
        handle_scrape_error(e)

@router.post("/scrape/ubuy")
def debug_scrape_ubuy(req: UbuyRequest):
    """
    Test the Ubuy scraper in isolation.
    Input format: Full Ubuy product URL (e.g., https://www.ubuy.co.in/product/...) and a region string (e.g., 'in', 'us').
    """
    try:
        return check_ubuy_stock(req.url, req.region)
    except Exception as e:
        handle_scrape_error(e)

@router.post("/scrape/walmart")
def debug_scrape_walmart(req: WalmartRequest):
    """
    Test the Walmart scraper in isolation.
    Input format: Walmart Item ID only, e.g. 123456789, not a full URL. (Use the 'url' field for this ID).
    """
    try:
        return check_walmart_price(req.url)
    except Exception as e:
        handle_scrape_error(e)

@router.post("/scrape/ebay")
def debug_scrape_ebay(req: EbayRequest):
    """
    Test the eBay scraper in isolation.
    Input format: eBay Item ID only, e.g. 123456789012, not a full URL. (Use the 'url' field for this ID).
    """
    try:
        return check_ebay_price(req.url)
    except Exception as e:
        handle_scrape_error(e)
