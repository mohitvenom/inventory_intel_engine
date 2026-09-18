import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import Product, SourceEnum

def seed_data():
    db = SessionLocal()
    
    # 5 Sample Products
    products = [
        Product(
            source=SourceEnum.amazon,
            external_id="B08N5WRWNW",
            name="Apple Mac Mini with Apple M1 Chip",
            currency="USD",
            price_drop_threshold_pct=5.0,
        ),
        Product(
            source=SourceEnum.amazon,
            external_id="B09G9FPHY6",
            name="Apple iPhone 13 Pro (128GB)",
            currency="USD",
            price_drop_threshold_pct=10.0,
        ),
        Product(
            source=SourceEnum.ubuy,
            external_id="https://www.ubuy.hk/en/product/12345-some-item",
            region="HK",
            name="Sony WH-1000XM4 Wireless Headphones",
            currency="HKD",
            price_drop_threshold_pct=8.0,
        ),
        Product(
            source=SourceEnum.ubuy,
            external_id="https://www.ubuy.ng/en/product/67890-another-item",
            region="NG",
            name="Logitech MX Master 3 Mouse",
            currency="NGN",
            price_drop_threshold_pct=15.0,
        ),
        Product(
            source=SourceEnum.amazon,
            external_id="B0B428M7NT",
            name="Kindle Paperwhite (8 GB)",
            currency="USD",
            price_drop_threshold_pct=5.0,
            notify_on_restock=False,
        ),
    ]

    for p in products:
        db.add(p)
        
    db.commit()
    print("Seed data inserted successfully.")
    
    db.close()

if __name__ == "__main__":
    seed_data()
