from app import app, db
from sqlalchemy import inspect
import os

def migrate():
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Create FundTransaction table if it doesn't exist
        if 'fund_transaction' not in inspector.get_table_names():
            print("Creating fund_transaction table...")
            db.create_all()
            print("Table created successfully.")
        else:
            print("fund_transaction table already exists.")

if __name__ == "__main__":
    migrate()
