import re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

from .types import ScrapeResult, ParseError, RateLimitedError
from .http import make_request_with_backoff

def check_walmart_price(external_id: str) -> ScrapeResult:
    url = f"https://www.walmart.com/ip/{external_id}"
    html = make_request_with_backoff(url, use_cloudscraper=True)
    
    # Walmart blocks cloudscraper often and returns a perimeterx page.
    if "Verify your identity" in html or "px-captcha" in html or "robot" in html.lower():
        raise RateLimitedError("Walmart blocked the request (PerimeterX/Captcha).")
        
    soup = BeautifulSoup(html, "html.parser")
    title_element = soup.find("h1", {"itemprop": "name"})
    if not title_element:
        # Fallback to standard title tag if h1 is obfuscated
        title_tag = soup.find("title")
        if title_tag and "Walmart.com" in title_tag.get_text():
            title = title_tag.get_text().replace(" - Walmart.com", "").strip()
        else:
            raise ParseError(f"Could not find product title on Walmart page for {external_id}")
    else:
        title = title_element.get_text(strip=True)
    
    price_element = soup.find("span", {"itemprop": "price"})
    price = None
    currency = "USD"
    if price_element:
        try:
            price = float(price_element.get_text(strip=True).replace("$", "").replace(",", ""))
        except:
            pass
            
    if not price:
        # Try to find string with $ 
        price_tags = soup.find_all("span", class_=re.compile("price", re.I))
        for pt in price_tags:
            text = pt.get_text(strip=True)
            if "$" in text:
                clean_price = re.sub(r'[^\d.]', '', text)
                if clean_price:
                    try:
                        price = float(clean_price)
                        break
                    except:
                        pass
                        
    in_stock = True
    if "Out of stock" in html or "not available" in html:
        in_stock = False
        
    if in_stock and price is None:
        raise ParseError(f"Product appears in stock but price could not be parsed for Walmart {external_id}")
        
    return ScrapeResult(
        source="walmart",
        external_id=external_id,
        region=None,
        price=price,
        currency=currency,
        in_stock=in_stock,
        title=title,
        checked_at=datetime.now(timezone.utc)
    )
