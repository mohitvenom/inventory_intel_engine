from backend.scrapers.http import make_request_with_backoff
import re
html = make_request_with_backoff('https://www.ubuy.co.in/en/product/12345', use_cloudscraper=True)
match = re.search(r'"price"\s*:\s*"?([\d\.]+)"?', html)
print('Regex price:', match.group(1) if match else None)
