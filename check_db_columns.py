from app import app, db
from sqlalchemy import text

def check_columns():
    with app.app_context():
        tables = ['relief_distribution', 'disaster', 'social_security_beneficiary', 'event_log', 'situation_report', 'public_information']
        for table in tables:
            try:
                result = db.session.execute(text(f"PRAGMA table_info({table})"))
                columns = [row[1] for row in result.fetchall()]
                print(f"Table: {table}")
                print(f"Columns: {columns}")
                if 'is_locked' in columns:
                    print(f"✅ is_locked exists in {table}")
                else:
                    print(f"❌ is_locked MISSING in {table}")
            except Exception as e:
                print(f"Error checking {table}: {e}")

if __name__ == "__main__":
    check_columns()
