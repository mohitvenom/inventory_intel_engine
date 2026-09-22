import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from .types import ScrapeResult, ParseError, RateLimitedError
from .http import make_request_with_backoff

def check_ebay_price(external_id: str) -> ScrapeResult:
    url = f"https://www.ebay.com/itm/{external_id}"
    html = make_request_with_backoff(url, use_cloudscraper=True)
    
    if "Security Measure" in html or "captcha" in html.lower():
        raise RateLimitedError("eBay blocked the request.")
        
    soup = BeautifulSoup(html, "html.parser")
    
    title_el = soup.select_one(".x-item-title__mainTitle span")
    if not title_el:
        # Fallback
        title_el = soup.find("title")
        if not title_el:
            raise ParseError(f"Could not find product title on eBay page for {external_id}")
        title = title_el.get_text(strip=True).replace(" | eBay", "")
    else:
        title = title_el.get_text(strip=True)
    
    price_el = soup.select_one(".x-price-primary .ux-textspans")
    price = None
    currency = "USD"
    if price_el:
        price_text = price_el.get_text(strip=True)
        if "£" in price_text:
            currency = "GBP"
        elif "€" in price_text:
            currency = "EUR"
        elif "C $" in price_text:
            currency = "CAD"
        elif "AU $" in price_text:
            currency = "AUD"
            
        clean_price = re.sub(r'[^\d.]', '', price_text)
        if clean_price:
            price = float(clean_price)
            
    in_stock = True
    if "Out of stock" in html or "This listing was ended" in html:
        in_stock = False
        
    if in_stock and price is None:
        raise ParseError(f"Product appears in stock but price could not be parsed for eBay {external_id}")
        
    return ScrapeResult(
        source="ebay",
        external_id=external_id,
        region=None,
        price=price,
        currency=currency,
        in_stock=in_stock,
        title=title,
        checked_at=datetime.now(timezone.utc)
    )
