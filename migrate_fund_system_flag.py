from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            db.session.execute(text("SELECT is_system FROM fund_transaction LIMIT 1"))
            print("Column 'is_system' already exists.")
        except Exception:
            print("Adding 'is_system' to 'fund_transaction'...")
            db.session.execute(text("ALTER TABLE fund_transaction ADD COLUMN is_system BOOLEAN DEFAULT FALSE"))
            db.session.execute(text("UPDATE fund_transaction SET is_system = FALSE"))
            # Update existing distribution transactions to be system generated
            db.session.execute(text("UPDATE fund_transaction SET is_system = TRUE WHERE id IN (SELECT fund_transaction_id FROM relief_distribution WHERE fund_transaction_id IS NOT NULL)"))
            db.session.commit()
            print("Migration successful.")

if __name__ == "__main__":
    migrate()
