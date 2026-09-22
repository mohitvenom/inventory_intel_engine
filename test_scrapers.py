import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from backend.scrapers.walmart import check_walmart_price
from backend.scrapers.ebay import check_ebay_price

# Real Walmart Item: https://www.walmart.com/ip/Nintendo-Switch-OLED-Model-w-White-Joy-Con/910582148
walmart_id = "910582148"
print("Testing Walmart...")
try:
    res = check_walmart_price(walmart_id)
    print("Walmart Success:", res)
except Exception as e:
    print("Walmart Error:", str(e))

# Real eBay Item: https://www.ebay.com/itm/145892556534
ebay_id = "145892556534"
print("\nTesting eBay...")
try:
    res = check_ebay_price(ebay_id)
    print("eBay Success:", res)
except Exception as e:
    print("eBay Error:", str(e))
