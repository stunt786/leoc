"""
LEOC SQLite -> PostgreSQL Data Migration Script

Usage:
    # 1. Set up PostgreSQL and configure .env with SQLALCHEMY_DATABASE_URI=postgresql://...
    # 2. Run: python migrate_to_postgres.py

This script:
    1. Connects to the existing SQLite database
    2. Creates all tables in PostgreSQL via init_db
    3. Reads all data from SQLite and inserts into PostgreSQL
"""

import os
import sys
import json
from datetime import datetime, date, time
from decimal import Decimal

os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('SECRET_KEY', 'migration-temp-key')

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'leoc.db')


def load_sqlite_data():
    """Read all data from SQLite into a portable dict."""
    import sqlite3
    if not os.path.exists(SQLITE_PATH):
        print(f"[!] SQLite database not found at {SQLITE_PATH}")
        print("[!] Run this script from the project root with the SQLite DB in place.")
        sys.exit(1)

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()
              if not row[0].startswith('sqlite_') and row[0] != 'alembic_version']

    data = {}
    for table in tables:
        cursor.execute(f'SELECT * FROM "{table}"')
        rows = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            for k, v in row_dict.items():
                if isinstance(v, (datetime, date)):
                    row_dict[k] = v.isoformat()
                elif isinstance(v, Decimal):
                    row_dict[k] = float(v)
            rows.append(row_dict)
        if rows:
            data[table] = rows
        print(f"  [READ] {table}: {len(rows)} rows")

    conn.close()
    return data


def _boolean_columns(table_name, inspector):
    """Return set of column names that are BOOLEAN type for a given table."""
    cols = inspector.get_columns(table_name)
    return {c['name'] for c in cols if str(c.get('type', '')).upper() == 'BOOLEAN'}


def migrate(data, target_uri):
    """Write data to PostgreSQL."""
    from app import app, db
    from init_db import create_tables, seed_all_data, create_user_table
    from sqlalchemy import inspect, text as sa_text
    from werkzeug.security import generate_password_hash

    app.config['SQLALCHEMY_DATABASE_URI'] = target_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.session.remove()
        from init_db import drop_all_tables
        drop_all_tables()

        print("\n[STEP] Creating tables in PostgreSQL...")
        create_tables()

        print("\n[STEP] Inserting data...")
        model_map = {}
        for mapper in db.Model.registry.mappers:
            table_name = mapper.entity.__tablename__ if hasattr(mapper.entity, '__tablename__') else None
            if table_name:
                model_map[table_name] = mapper.entity

        pg_inspector = inspect(db.engine)

        table_order = [
            'user', 'ward', 'category', 'app_settings',
            'warehouse', 'warehouse_zone', 'supplier',
            'item', 'beneficiary',
            'incident', 'stock_receipt', 'stock_receipt_item', 'stock_receipt_attachment',
            'inventory', 'manual_adjustment',
            'relief_request', 'relief_request_item',
            'dispatch', 'dispatch_item',
            'distribution', 'distribution_beneficiary',
            'stock_transfer', 'stock_transfer_item',
            'cash_fund', 'cash_receipt', 'cash_request',
            'cash_distribution', 'cash_distribution_beneficiary',
            'disaster_assessment',
            'daily_report_log', 'daily_bulletin', 'weekly_forecast',
            'activity_log', 'document_archive',
        ]

        total_rows = sum(len(rows) for rows in data.values())
        inserted = 0

        for table in table_order:
            if table not in data:
                continue
            rows = data[table]
            bool_cols = _boolean_columns(table, pg_inspector) if table != 'user' else set()

            if table == 'user':
                for row_data in rows:
                    db.session.execute(
                        sa_text("""
                            INSERT INTO "user" (username, password_hash, role, full_name, is_active, created_at, last_login, failed_login_attempts, locked_until)
                            VALUES (:username, :password_hash, :role, :full_name, :is_active, :created_at, :last_login, :failed_login_attempts, :locked_until)
                        """),
                        {
                            'username': row_data['username'],
                            'password_hash': row_data['password_hash'],
                            'role': row_data.get('role', 'viewer'),
                            'full_name': row_data.get('full_name'),
                            'is_active': bool(row_data.get('is_active', 1)),
                            'created_at': row_data.get('created_at'),
                            'last_login': row_data.get('last_login'),
                            'failed_login_attempts': row_data.get('failed_login_attempts', 0),
                            'locked_until': row_data.get('locked_until'),
                        }
                    )
                    inserted += 1
                db.session.commit()
                print(f"  [OK] {table}: {len(rows)} rows inserted (raw SQL)")
                continue

            model = model_map.get(table)
            if not model:
                print(f"  [SKIP] {table}: no matching model")
                continue

            for row_data in rows:
                for bc in bool_cols:
                    if bc in row_data and isinstance(row_data[bc], int):
                        row_data[bc] = bool(row_data[bc])
                try:
                    obj = model(**row_data)
                    db.session.add(obj)
                    inserted += 1
                except Exception as e:
                    print(f"  [WARN] {table}: {e}")
            db.session.commit()
            print(f"  [OK] {table}: {len(rows)} rows inserted")

        print(f"\n[SUMMARY] Inserted {inserted}/{total_rows} rows into PostgreSQL")

        print("\n[STEP] Seeding default data (categories, settings, wards if missing)...")
        seed_all_data()


if __name__ == '__main__':
    target = os.getenv('SQLALCHEMY_DATABASE_URI')
    if not target or 'postgresql' not in target:
        print("[!] Set SQLALCHEMY_DATABASE_URI to your PostgreSQL URI first.")
        print("    Example: export SQLALCHEMY_DATABASE_URI=postgresql://leoc:pass@localhost:5432/leoc")
        sys.exit(1)

    print(f"[*] Migrating from SQLite ({SQLITE_PATH})")
    print(f"[*] Target: {target}")
    print()

    data = load_sqlite_data()
    if not data:
        print("[!] No data found in SQLite database.")
        sys.exit(1)

    migrate(data, target)
    print("\n[✓] Migration complete!")
