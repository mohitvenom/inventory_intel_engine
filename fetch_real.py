import sys
import os
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.scrapers.http import make_request_with_backoff

try:
    amazon_html = make_request_with_backoff("https://www.amazon.com/dp/B08J5F3G18", use_cloudscraper=True)
    with open("tests/fixtures/real_amazon.html", "w", encoding="utf-8") as f:
        f.write(amazon_html)
except Exception as e:
    print(e)

try:
    ubuy_html = make_request_with_backoff("https://www.ubuy.hk/en/product/4373O20-sony-mdr-e9lp-earbud-headphones-black", use_cloudscraper=True)
    with open("tests/fixtures/real_ubuy.html", "w", encoding="utf-8") as f:
        f.write(ubuy_html)
except Exception as e:
    print(e)
