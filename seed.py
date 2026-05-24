"""
app/database/seed.py
====================
Table creation + demo data seeding. Called once at startup.
"""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.database.connection import engine
from app.database.models import Base, Product


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("[DB] Tables ensured ✓")


def seed_demo_data(db: Session) -> None:
    if db.query(Product).count() > 0:
        print("[DB] Demo data already present, skipping seed.")
        return
    sample_products = [
        Product(name="Mechanical Keyboard",  description="RGB backlit, tactile switches", price=4999.0, stock=50,  category="Electronics"),
        Product(name="Wireless Mouse",        description="Ergonomic, 2.4GHz",             price=1299.0, stock=120, category="Electronics"),
        Product(name="USB-C Hub 7-in-1",      description="4K HDMI, PD charging",          price=2499.0, stock=75,  category="Electronics"),
        Product(name="Laptop Stand",          description="Aluminium, adjustable height",   price=1799.0, stock=60,  category="Accessories"),
        Product(name="Noise-Cancelling Buds", description="40hr battery, ANC",              price=6999.0, stock=30,  category="Audio"),
        Product(name="Webcam 1080p",          description="Auto-focus, ring light",         price=3499.0, stock=45,  category="Electronics"),
        Product(name="Monitor Light Bar",     description="USB powered, dimmable",          price=999.0,  stock=90,  category="Accessories"),
        Product(name="Desk Mat XL",           description="900x400mm, stitched edges",      price=799.0,  stock=200, category="Accessories"),
        Product(name="Cable Management Kit",  description="Velcro + clips + sleeve",        price=399.0,  stock=300, category="Accessories"),
        Product(name="Smart Power Strip",     description="6 outlets, surge protected",     price=1599.0, stock=55,  category="Electronics"),
    ]
    db.add_all(sample_products)
    db.commit()
    print(f"[DB] Seeded {len(sample_products)} demo products ✓")
