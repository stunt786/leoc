import os
import tempfile
import unittest
import uuid
import atexit
from datetime import datetime, timezone


_db_fd, _db_path = tempfile.mkstemp(prefix='leoc_', suffix='.sqlite')
os.close(_db_fd)
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('ADMIN_PASSWORD', 'admin123')
os.environ.setdefault('MANAGER_PASSWORD', 'manager123')
os.environ.setdefault('DATAENTRY_PASSWORD', 'dataentry123')
os.environ.setdefault('VIEWER_PASSWORD', 'viewer123')
os.environ.setdefault('OPERATOR_PASSWORD', 'operator123')
os.environ.setdefault('FINANCE_PASSWORD', 'finance123')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'
os.environ['RATELIMIT_ENABLED'] = 'False'

import app as app_module
from app import Ward, db as _db


def _cleanup():
    try:
        os.remove(_db_path)
    except (FileNotFoundError, OSError):
        pass


atexit.register(_cleanup)


def _seed_test_wards():
    if Ward.query.first() is None:
        for i in range(1, 10):
            _db.session.add(Ward(name=f'Ward {i}', sort_order=i))
        _db.session.commit()


with app_module.app.app_context():
    _seed_test_wards()


class LeocTestCase(unittest.TestCase):
    def setUp(self):
        app_module.app.config['TESTING'] = True
        app_module.app.config['WTF_CSRF_ENABLED'] = False
        app_module.app.config['SERVER_NAME'] = 'localhost'
        app_module.limiter.enabled = False
        self.client = app_module.app.test_client()
        app_module.clear_cache()

    def login(self, username='admin', password='admin123'):
        return self.client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=False,
        )

    def login_as(self, role='admin'):
        creds = {
            'admin': ('admin', 'admin123'),
            'viewer': ('viewer', 'viewer123'),
            'data_entry': ('dataentry', 'dataentry123'),
            'warehouse_manager': ('warehousemgr', 'manager123'),
            'editor': ('editor1', 'editor123'),
            'operator': ('operator1', 'operator123'),
            'finance': ('finance1', 'finance123'),
        }
        username, password = creds.get(role, creds['admin'])
        rv = self.client.post('/login', data={'username': username, 'password': password}, follow_redirects=False)
        if rv.status_code not in (302, 200):
            rv = self.login(username, password)
        return rv

    def create_user_direct(self, username, password='password123', role='viewer', full_name='Test User'):
        with app_module.app.app_context():
            from werkzeug.security import generate_password_hash
            app_module.db.session.execute(
                app_module.db.text(
                    'INSERT INTO "user" (username, password_hash, role, full_name, is_active, created_at) '
                    'VALUES (:username, :password_hash, :role, :full_name, :is_active, :created_at)'
                ),
                {
                    'username': username,
                    'password_hash': generate_password_hash(password),
                    'role': role,
                    'full_name': full_name,
                    'is_active': True,
                    'created_at': datetime.now(timezone.utc),
                },
            )
            app_module.db.session.commit()

    def create_category(self, name=None, description='Test category'):
        payload = {
            'name': name or f'Cat-{uuid.uuid4().hex[:8]}',
            'description': description,
        }
        response = self.client.post('/api/categories', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_warehouse(self, name=None, capacity=1000):
        payload = {
            'name': name or f'Warehouse-{uuid.uuid4().hex[:8]}',
            'code': '',
            'address': 'Test address',
            'capacity': capacity,
            'remarks': 'Test warehouse',
        }
        response = self.client.post('/api/warehouses', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_supplier(self, name=None, phone=None, email=None):
        payload = {
            'name': name or f'Supplier-{uuid.uuid4().hex[:8]}',
            'phone': phone or f'98{str(uuid.uuid4().int)[:8]}',
            'email': email or f'supplier{uuid.uuid4().hex[:4]}@example.com',
            'address': 'Test supplier address',
        }
        response = self.client.post('/api/suppliers', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_item(self, category_id, name=None, unit='Piece', min_stock=2, max_stock=25):
        payload = {
            'name': name or f'Item-{uuid.uuid4().hex[:8]}',
            'unit': unit,
            'category_id': category_id,
            'minimum_stock': min_stock,
            'max_stock': max_stock,
            'storage_life_days': 365,
            'expiry_tracking': True,
            'batch_tracking': True,
            'is_consumable': True,
            'is_distributable': True,
            'storage_requirement': 'Normal',
        }
        response = self.client.post('/api/items', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_incident(self, name=None, incident_type='Flood', ward=1):
        payload = {
            'incident_name': name or f'Incident-{uuid.uuid4().hex[:8]}',
            'incident_type': incident_type,
            'ward': ward,
            'start_date': '2082-01-01',
            'status': 'Active',
            'description': 'Test incident',
            'coordinates': '28.5,81.5',
            'affected_households': 200,
        }
        response = self.client.post('/api/incidents', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_stock_receipt(self, warehouse_id, item_id, quantity=10, unit_cost=12.5):
        response = self.client.post(
            '/api/stock-receipts',
            json={
                'warehouse_id': warehouse_id,
                'source_type': 'Donation',
                'source_name': 'Test Donor',
                'date': '2082-03-01',
                'items': [{
                    'item_id': item_id,
                    'quantity': quantity,
                    'unit': 'Piece',
                    'unit_cost': unit_cost,
                    'mfg_date': '2081-09-01',
                    'expiry_date': '2083-09-01',
                }],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_distribution(self, warehouse_id, incident_id, item_id, quantity=4,
                            beneficiary_name='Family A', beneficiary_qty=2):
        payload = {
            'incident_id': incident_id,
            'warehouse_id': warehouse_id,
            'destination': 'Test Destination',
            'receiver': 'Test Receiver',
            'distribution_date': '2082-03-03',
            'officer': 'Test Officer',
            'remarks': 'Test distribution',
            'items': [{'item_id': item_id, 'warehouse_id': warehouse_id, 'quantity': quantity,
                       'unit': 'Piece', 'batch_no': 'BATCH-001', 'expiry_date': '2083-09-01'}],
            'beneficiaries': [
                {'family_name': beneficiary_name, 'members': 3, 'item': None, 'quantity': beneficiary_qty},
            ],
        }
        response = self.client.post('/api/distributions', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_beneficiary(self, name=None, national_id=None, ward=1, phone=None):
        payload = {
            'name': name or f'Ben-{uuid.uuid4().hex[:8]}',
            'national_id': national_id or f'NID-{uuid.uuid4().hex[:8]}',
            'father_name': 'Test Father',
            'phone': phone or f'98{uuid.uuid4().int % 100000000:08d}',
            'ward': ward,
            'tole': 'Test Tole',
            'family_members': 4,
            'address': 'Test Address',
        }
        response = self.client.post('/api/beneficiaries', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_fund(self, name=None, allocated=1000):
        payload = {
            'name': name or f'Fund-{uuid.uuid4().hex[:8]}',
            'fiscal_year': '2081/82',
            'funding_source': 'Municipality',
            'allocated_amount': allocated,
        }
        response = self.client.post('/api/cash-funds', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_cash_receipt(self, fund_id, amount=500):
        payload = {
            'fund_id': fund_id,
            'receipt_date': '2082-03-01',
            'amount_received': amount,
            'funding_source': 'Donation',
        }
        response = self.client.post('/api/cash-receipts', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_cash_request(self, incident_id, amount=300, beneficiary_id=None):
        if beneficiary_id is None:
            ben = self.create_beneficiary()
            beneficiary_id = ben['id']
        payload = {
            'incident_id': incident_id,
            'beneficiary_id': beneficiary_id,
            'requesting_office': 'Test Office',
            'requester_name': 'Test Requester',
            'phone': '9800000000',
            'priority': 'High',
            'requested_amount': amount,
            'purpose': 'Emergency assistance',
            'remarks': 'Test cash request',
            'request_date': '2082-03-01',
        }
        response = self.client.post('/api/cash-requests', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_cash_distribution(self, fund_id, incident_id, cash_request_id=None, amount=300, beneficiary_ids=None):
        if beneficiary_ids is None:
            b1 = self.create_beneficiary()
            b2 = self.create_beneficiary()
            beneficiary_ids = [b1['id'], b2['id']]
        beneficiaries = [
            {'name': f'Cash-{uuid.uuid4().hex[:8]}', 'national_id': f'NID-{uuid.uuid4().hex[:8]}',
             'amount': amount // 3, 'beneficiary_id': beneficiary_ids[0]},
            {'name': f'Cash-{uuid.uuid4().hex[:8]}', 'national_id': f'NID-{uuid.uuid4().hex[:8]}',
             'amount': amount - amount // 3, 'beneficiary_id': beneficiary_ids[1]},
        ]
        payload = {
            'fund_id': fund_id,
            'incident_id': incident_id,
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-03',
            'officer': 'Test Officer',
            'remarks': 'Test cash distribution',
            'beneficiaries': beneficiaries,
        }
        response = self.client.post('/api/cash-distributions', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']
