from app import app, db
from sqlalchemy import text
import os

def migrate():
    with app.app_context():
        # Check if column exists first
        try:
            db.session.execute(text("SELECT is_locked FROM fund_transaction LIMIT 1"))
            print("Column 'is_locked' already exists.")
        except Exception:
            print("Adding 'is_locked' to 'fund_transaction'...")
            db.session.execute(text("ALTER TABLE fund_transaction ADD COLUMN is_locked BOOLEAN DEFAULT FALSE"))
            db.session.execute(text("UPDATE fund_transaction SET is_locked = FALSE"))
            db.session.execute(text("CREATE INDEX ix_fund_transaction_is_locked ON fund_transaction (is_locked)"))
            db.session.commit()
            print("Migration successful.")

if __name__ == "__main__":
    migrate()
