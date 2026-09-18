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
            name="EVGA GeForce RTX 3090",
            source=SourceEnum.amazon,
            external_id="B08J5F3G18",
            is_active=True
        ),
        Product(
            name="LG 27UK850-W 27\" 4K UHD IPS Monitor",
            source=SourceEnum.amazon,
            external_id="B078GRRVVW",
            is_active=True
        ),
        Product(
            name="Birthday Gifts for Women Spa Package",
            source=SourceEnum.ubuy,
            external_id="https://www.ubuy.hk/en/product/MJKMFA9O6-birthday-gifts-for-women-get-well-gifts-for-women-relaxing-spa-gifts-care-package-with-luxury-flannel-blanket-light-up-rose-flower-unique-self",
            is_active=True
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
