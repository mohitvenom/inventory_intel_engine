import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import Product, SourceEnum

def seed_data():
    db = SessionLocal()
    
    products = [
        Product(
            name="2020 Apple MacBook Air Laptop: Apple M1 Chip, 13 Retina Display, 8GB RAM, 256GB SSD Storage, Backlit Keyboard, FaceTime HD Camera, Touch ID. Works with iPhone/iPad; Space Gray",
            source=SourceEnum.amazon,
            external_id="B08N5LNQCX",
            region=None,
            currency="USD",
            price_drop_threshold_pct=5.0,
            notify_on_restock=True,
            notify_on_stockout=False,
            active=True
        ),
        Product(
            name="Apple iPad (9th Generation): with A13 Bionic chip, 10.2-inch Retina Display, 64GB, Wi-Fi, 12MP front/8MP Back Camera, Touch ID, All-Day Battery Life – Space Gray",
            source=SourceEnum.amazon,
            external_id="B09G9FPHY6",
            region=None,
            currency="USD",
            price_drop_threshold_pct=10.0,
            notify_on_restock=True,
            notify_on_stockout=True,
            active=True
        ),
        Product(
            name="EVGA GeForce RTX 3090 FTW3 Ultra Gaming, 24GB GDDR6X, iCX3 Technology, ARGB LED, Metal Backplate, 24G-P5-3987-KR",
            source=SourceEnum.amazon,
            external_id="B08J5F3G18",
            region=None,
            currency="USD",
            price_drop_threshold_pct=15.0,
            notify_on_restock=False,
            notify_on_stockout=True,
            active=True
        ),
        Product(
            name="Birthday and Get Well Gifts for Women - Relaxing Spa Care Package",
            source=SourceEnum.ubuy,
            external_id="https://www.ubuy.hk/en/product/MJKMFA9O6-birthday-gifts",
            region="hk",
            currency="HKD",
            price_drop_threshold_pct=5.0,
            notify_on_restock=True,
            notify_on_stockout=False,
            active=True
        ),
        Product(
            name="Champion Long T-Shirt 100% Cotton One Point Logo Long Sleeve T-Shirt Women's CW-T404",
            source=SourceEnum.ubuy,
            external_id="https://www.ubuy.co.in/en/product/12345",
            region="in",
            currency="INR",
            price_drop_threshold_pct=5.0,
            notify_on_restock=True,
            notify_on_stockout=False,
            active=True
        )
    ]
    db.add_all(products)
    db.commit()
    print("Seed data inserted successfully.")
    
    db.close()

if __name__ == "__main__":
    seed_data()
