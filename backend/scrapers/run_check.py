import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.session import SessionLocal
from backend.db.models import Product
from backend.scrapers.amazon import check_amazon_price
from backend.scrapers.ubuy import check_ubuy_stock
from backend.scrapers.types import ScrapeError

def main():
    parser = argparse.ArgumentParser(description="Manual smoke-test for scrapers")
    parser.add_argument("product_id", type=int, help="The ID of the product in the database")
    args = parser.parse_args()
    
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == args.product_id).first()
    db.close()
    
    if not product:
        print(f"Product with ID {args.product_id} not found.")
        sys.exit(1)
        
    print(f"Found product: {product.name} (Source: {product.source})")
    
    try:
        if product.source == "amazon":
            print(f"Running Amazon scraper for ASIN: {product.external_id}...")
            result = check_amazon_price(product.external_id)
        elif product.source == "ubuy":
            print(f"Running Ubuy scraper for URL: {product.external_id}...")
            result = check_ubuy_stock(product.external_id, product.region)
        else:
            print(f"Unknown source: {product.source}")
            sys.exit(1)
            
        print("\n--- Scrape Result ---")
        print(f"Title: {result.title}")
        print(f"In Stock: {result.in_stock}")
        print(f"Price: {result.price} {result.currency if result.price else ''}")
        print(f"Checked At: {result.checked_at}")
        
    except ScrapeError as e:
        print(f"\n--- Scrape Failed ---")
        print(f"Error type: {type(e).__name__}")
        print(f"Message: {e}")
        
if __name__ == "__main__":
    main()
