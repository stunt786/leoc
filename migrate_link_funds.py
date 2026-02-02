from app import app, db
from sqlalchemy import text
import os

def migrate():
    with app.app_context():
        # Check if column exists first
        try:
            db.session.execute(text("SELECT fund_transaction_id FROM relief_distribution LIMIT 1"))
            print("Column 'fund_transaction_id' already exists.")
        except Exception:
            print("Adding 'fund_transaction_id' to 'relief_distribution'...")
            db.session.execute(text("ALTER TABLE relief_distribution ADD COLUMN fund_transaction_id INTEGER REFERENCES fund_transaction(id)"))
            db.session.commit()
            print("Migration successful.")

if __name__ == "__main__":
    migrate()
