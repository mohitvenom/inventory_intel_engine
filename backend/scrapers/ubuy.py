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

    # 2. Extract Javascript Variables for AJAX
    vars_dict = {}
    for script in soup.find_all('script'):
        text = script.string
        if text and 'csrftoken_common' in text:
            for line in text.split(';'):
                line = line.strip()
                if line.startswith('var '):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        k = parts[0].replace('var', '').strip()
                        v = parts[1].strip().strip("'").strip('"')
                        vars_dict[k] = v

    in_stock = False
    price = None
    currency = None

    ajax_url = vars_dict.get('ajax_url')
    if ajax_url:
        import json
        import base64
        
        fetch_data = {
            'cur_url': vars_dict.get('current_url', ''),
            'id': vars_dict.get('entity_id', ''),
            'sku': vars_dict.get('selected_asin', ''),
            'v_sku': '',
            'p_sku': vars_dict.get('parent_asin', ''),
            'c_id': '',
            'sname': vars_dict.get('storename', 'US'),
            'sbname': vars_dict.get('substorename', 'usstore'),
            'is_ajax': False,
            'pid': vars_dict.get('product_id', ''),
            'sid': vars_dict.get('s_id', '61'),
            'can_url': vars_dict.get('canonical_url', ''),
            'lng': 'en',
            'dir': 'allstore',
            'fn': 'fetch',
            'd': 'd',
            'token': vars_dict.get('csrftoken_common', ''),
            'lv': 'v4',
            'c_u_p_s_id': ''
        }
        
        json_str = json.dumps(fetch_data)
        b64_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        # Need to construct the absolute AJAX URL if it's relative
        if ajax_url.startswith('/'):
            # This is a bit naive but ubuy ajax_url is usually absolute: "https://www.ubuy.com.es/en/detail_product"
            pass 
            
        try:
            # We must use make_request_with_backoff for the AJAX call as well to bypass cloudflare,
            # but make_request_with_backoff currently only supports GET without query params easily?
            # Wait, make_request_with_backoff takes `url` which can contain query params.
            full_ajax_url = f"{ajax_url}?fetch_data={b64_data}"
            ajax_html = make_request_with_backoff(full_ajax_url, use_cloudscraper=True)
            ajax_soup = BeautifulSoup(ajax_html, "html.parser")
            
            # Stock Status
            in_stock = "add to cart" in ajax_html.lower() or "add to bag" in ajax_html.lower()
            
            # Price & Currency
            price_element = ajax_soup.find(itemprop="price")
            if price_element and price_element.get("content"):
                try:
                    price = float(price_element["content"].replace(",", ""))
                except ValueError:
                    pass
            
            # Currency
            if vars_dict.get('cur'):
                currency_sym = vars_dict.get('cur').upper()
                if currency_sym == "€" or currency_sym == "EUR":
                    currency = "EUR"
                elif currency_sym == "$" or currency_sym == "USD":
                    currency = "USD"
                else:
                    currency = currency_sym
            
            # Fallback if no AJAX price found
            if price is None:
                price_box = ajax_soup.select_one('.price-amount')
                if price_box:
                    match = re.search(r"[\d,]+(?:\.\d+)?", price_box.get_text(strip=True))
                    if match:
                        try:
                            price = float(match.group().replace(",", ""))
                        except ValueError:
                            pass
        except Exception as e:
            print(f"Error fetching Ubuy AJAX: {e}")
            pass
            
    if currency is None:
        currency = f"{region.upper()}_CURRENCY"

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
