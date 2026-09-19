import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from .types import ScrapeResult, ParseError
from .http import make_request_with_backoff

def check_amazon_price(asin: str) -> ScrapeResult:
    """
    Fetches and parses an Amazon product page for price, title, and stock status.
    """
    url = f"https://www.amazon.com/dp/{asin}"
    html = make_request_with_backoff(url, use_cloudscraper=True)
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Title
    title_element = soup.find(id="productTitle")
    if not title_element:
        raise ParseError(f"Could not find product title on Amazon page for ASIN {asin}")
    title = title_element.get_text(strip=True)
    
    # 2. Stock Status & Price
    # Availability element typically has id "availability"
    availability_element = soup.find(id="availability")
    
    in_stock = True
    if availability_element:
        availability_text = availability_element.get_text(strip=True).lower()
        if "currently unavailable" in availability_text or "out of stock" in availability_text:
            in_stock = False
            
    # Sometimes Amazon has a specific out of stock div, but check if it's really OOS and not just shipping restrictions
    out_of_stock_div = soup.find(id="outOfStock")
    if out_of_stock_div:
        oos_text = out_of_stock_div.get_text(strip=True).lower()
        if "currently unavailable" in oos_text or "out of stock" in oos_text:
            in_stock = False

    price = None
    currency = "USD"
    
    # Extract price if in stock
    # Amazon uses multiple selectors for price:
    # .a-price > .a-offscreen, #priceblock_ourprice, #priceblock_dealprice
    price_element = soup.select_one('.a-price .a-offscreen')
    if not price_element:
        price_element = soup.find(id="priceblock_ourprice") or soup.find(id="priceblock_dealprice")
        
    if price_element:
        price_text = price_element.get_text(strip=True)
        # Assuming USD formatting e.g., "$19.99"
        match = re.search(r"[\d,]+\.\d{2}", price_text)
        if match:
            try:
                price = float(match.group().replace(",", ""))
            except ValueError:
                pass
                
    if in_stock and price is None:
        raise ParseError(f"Product appears in stock but price could not be parsed for ASIN {asin}")

    return ScrapeResult(
        source="amazon",
        external_id=asin,
        region=None,
        price=price,
        currency=currency,
        in_stock=in_stock,
        title=title,
        checked_at=datetime.now(timezone.utc)
    )
