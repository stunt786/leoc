from app import app, db
from sqlalchemy import text
import os

def migrate():
    with app.app_context():
        # Check if column exists first
        try:
            db.session.execute(text("SELECT item_code FROM inventory_item LIMIT 1"))
            print("Column 'item_code' already exists.")
        except Exception:
            print("Adding 'item_code' to 'inventory_item'...")
            db.session.execute(text("ALTER TABLE inventory_item ADD COLUMN item_code VARCHAR(50)"))
            db.session.execute(text("CREATE INDEX ix_inventory_item_item_code ON inventory_item (item_code)"))
            db.session.commit()
            print("Migration successful.")

if __name__ == "__main__":
    migrate()
