import os
import sys

# Ensure backend modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.mcp_server.server import (
    check_amazon_price,
    check_ubuy_stock,
    list_watchlist,
    get_price_history,
    get_stock_history,
    record_price_check,
    record_stock_check
)

def test_smoke():
    print("--- Testing list_watchlist ---")
    watchlist = list_watchlist(active_only=True)
    print(f"Found {len(watchlist)} active items.")
    for item in watchlist:
        print(f"  - {item['name']} ({item['source']})")
    
    print("\n--- Testing check_amazon_price (Real ASIN) ---")
    # Using the real ASIN we tested in pre-flight
    res_amazon = check_amazon_price('B08J5F3G18')
    print("Result:", res_amazon)

    print("\n--- Testing check_amazon_price (Bad ASIN) ---")
    res_bad = check_amazon_price('INVALID_ASIN_123')
    print("Result:", res_bad)
    
    print("\n--- Testing get_price_history (Before Record) ---")
    # Assuming product ID 1 exists
    hist = get_price_history(product_id=1, limit=5)
    print("History length before:", len(hist))
    
    print("\n--- Testing record_price_check ---")
    record = record_price_check(product_id=1, price=1499.99, currency="USD")
    print("Recorded:", record)
    
    print("\n--- Testing get_price_history (After Record) ---")
    hist_after = get_price_history(product_id=1, limit=5)
    print("History length after:", len(hist_after))
    if hist_after:
        print("Most recent record:", hist_after[0])

if __name__ == "__main__":
    test_smoke()
