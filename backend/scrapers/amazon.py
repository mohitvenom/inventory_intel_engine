import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from .types import ScrapeResult, ParseError, RegionRestrictedError
from .http import make_request_with_backoff
import requests

def check_amazon_price(asin: str, region: str = "com") -> ScrapeResult:
    """
    Fetches and parses an Amazon product page for price, title, and stock status.
    Uses the specified region (default 'com') to build the correct domain (e.g., 'in', 'co.uk').
    For 'com' region, enforces zip code 41018 (Erlanger, KY) to get accurate US pricing/stock.
    """
    domain = f"amazon.{region}" if region else "amazon.com"
    url = f"https://www.{domain}/dp/{asin}"
    
    session = requests.Session()
    if domain == "amazon.com":
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            }
            # 1. Get initial session cookies
            session.get("https://www.amazon.com/", headers=headers, timeout=10)
            # 2. Set zip code to 41018
            post_headers = headers.copy()
            post_headers["Content-Type"] = "application/x-www-form-urlencoded"
            post_headers["X-Requested-With"] = "XMLHttpRequest"
            data = {
                "locationType": "LOCATION_INPUT",
                "zipCode": "41018",
                "storeContext": "generic",
                "deviceType": "web",
                "pageType": "Search",
                "actionSource": "glow"
            }
            session.post("https://www.amazon.com/gp/delivery/ajax/address-change.html", headers=post_headers, data=data, timeout=10)
        except Exception:
            pass
            
    html = make_request_with_backoff(url, use_cloudscraper=False, session=session)
    
    # Check for CAPTCHA block
    if "validateCaptcha" in html or "api-services-support@amazon.com" in html:
        from .types import RateLimitedError
        raise RateLimitedError("Amazon blocked the request (Captcha).")
        
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
        elif "cannot be shipped" in availability_text:
            raise RegionRestrictedError(f"Product cannot be shipped to the current region: {asin}")
            
    # Sometimes Amazon has a specific out of stock div, but check if it's really OOS and not just shipping restrictions
    out_of_stock_div = soup.find(id="outOfStock")
    if out_of_stock_div:
        oos_text = out_of_stock_div.get_text(strip=True).lower()
        if "currently unavailable" in oos_text or "out of stock" in oos_text:
            in_stock = False
        elif "cannot be shipped" in oos_text:
            raise RegionRestrictedError(f"Product cannot be shipped to the current region: {asin}")

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
        if "TRY" in price_text or "₺" in price_text:
            currency = "TRY"
        elif "£" in price_text:
            currency = "GBP"
        elif "€" in price_text:
            currency = "EUR"
        elif "₹" in price_text:
            currency = "INR"
        else:
            currency = "USD"
            
        # Amazon often breaks price into whole and fraction without a decimal in .a-offscreen
        whole = price_element.parent.find(class_="a-price-whole")
        fraction = price_element.parent.find(class_="a-price-fraction")
        
        if whole and fraction:
            whole_text = re.sub(r'[^\d]', '', whole.get_text())
            fraction_text = re.sub(r'[^\d]', '', fraction.get_text())
            if whole_text and fraction_text:
                price = float(f"{whole_text}.{fraction_text}")
        
        if price is None:
            clean_price = re.sub(r'[^\d.,]', '', price_text)
            if clean_price:
                if ',' in clean_price and '.' in clean_price:
                    if clean_price.rfind(',') > clean_price.rfind('.'):
                        clean_price = clean_price.replace('.', '').replace(',', '.')
                    else:
                        clean_price = clean_price.replace(',', '')
                elif ',' in clean_price:
                    clean_price = clean_price.replace(',', '.')
                try:
                    price = float(clean_price)
                except ValueError:
                    pass
                
    if in_stock and price is None:
        raise ParseError(f"Product appears in stock but price could not be parsed for ASIN {asin}")

    return ScrapeResult(
        source="amazon",
        external_id=asin,
        region=region,
        price=price,
        currency=currency,
        in_stock=in_stock,
        title=title,
        checked_at=datetime.now(timezone.utc)
    )
