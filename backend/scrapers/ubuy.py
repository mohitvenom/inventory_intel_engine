import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from .types import ScrapeResult, ParseError
from .http import make_request_with_backoff

def check_ubuy_stock(product_url: str, region: str) -> ScrapeResult:
    """
    Fetches and parses a Ubuy product page for stock status and optional price.
    Uses cloudscraper to bypass potential Cloudflare protections.
    """
    html = make_request_with_backoff(product_url, use_cloudscraper=True)
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Title
    title_element = soup.find("h1", class_=lambda c: c and ("product-title" in c or "description" in c))
    if not title_element:
        title_element = soup.find("h2", class_=lambda c: c and "title" in c)
        
    title = title_element.get_text(strip=True) if title_element else None
    if not title:
        raise ParseError(f"Could not find product title on Ubuy page: {product_url}")

    # 2. Stock Status
    in_stock = True
    
    # Check for "Out of stock" text in the availability section
    availability_elements = soup.find_all(string=re.compile(r"out of stock", re.IGNORECASE))
    if availability_elements:
        in_stock = False

    # 3. Price (Optional)
    price = None
    currency = None
    
    # Ubuy typically shows price in a span with class "price" or similar
    price_element = soup.select_one('.product-price') or soup.find(class_=lambda c: c and "price" in c)
    
    if price_element:
        price_text = price_element.get_text(strip=True)
        # Just grab the first sequence of numbers, commas, and dots
        # E.g. "HKD 1,234.56" -> "1,234.56"
        match = re.search(r"[\d,]+(?:\.\d+)?", price_text)
        if match:
            try:
                price = float(match.group().replace(",", ""))
                
                # Try to guess currency from the text, otherwise fallback to the region code (imperfect but OK)
                if "HKD" in price_text.upper() or "HK$" in price_text:
                    currency = "HKD"
                elif "NGN" in price_text.upper() or "₦" in price_text:
                    currency = "NGN"
                else:
                    currency = f"{region.upper()}_CURRENCY"  # Fallback
            except ValueError:
                pass

    return ScrapeResult(
        source="ubuy",
        external_id=product_url,
        region=region,
        price=price,
        currency=currency,
        in_stock=in_stock,
        title=title,
        checked_at=datetime.now(timezone.utc)
    )
