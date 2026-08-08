import os
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone


_db_fd, _db_path = tempfile.mkstemp(prefix='leoc_auth_', suffix='.sqlite')
os.close(_db_fd)
os.environ.setdefault('SECRET_KEY', 'auth-test-secret')
os.environ.setdefault('ADMIN_PASSWORD', 'admin123')
os.environ.setdefault('MANAGER_PASSWORD', 'manager123')
os.environ.setdefault('DATAENTRY_PASSWORD', 'dataentry123')
os.environ.setdefault('VIEWER_PASSWORD', 'viewer123')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'

import app as app_module


def _seed_test_wards():
    from app import Ward, db
    if Ward.query.first() is None:
        for i in range(1, 10):
            db.session.add(Ward(name=f'Ward {i}', sort_order=i))
        db.session.commit()


class AuthValidationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with app_module.app.app_context():
            _seed_test_wards()

    @classmethod
    def tearDownClass(cls):
        with app_module.app.app_context():
            app_module.db.session.remove()
            app_module.db.engine.dispose()
        try:
            os.remove(_db_path)
        except FileNotFoundError:
            pass

    def setUp(self):
        app_module.app.config['TESTING'] = True
        app_module.app.config['WTF_CSRF_ENABLED'] = False
        self.client = app_module.app.test_client()

    def login(self, username='admin', password='admin123'):
        return self.client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=False,
        )

    def create_user(self, username, password='password123', role='viewer', full_name='Test User'):
        with app_module.app.app_context():
            app_module.db.session.execute(
                app_module.db.text(
                    'INSERT INTO "user" (username, password_hash, role, full_name, is_active, created_at) '
                    'VALUES (:username, :password_hash, :role, :full_name, :is_active, :created_at)'
                ),
                {
                    'username': username,
                    'password_hash': app_module.generate_password_hash(password),
                    'role': role,
                    'full_name': full_name,
                    'is_active': True,
                    'created_at': datetime.now(timezone.utc),
                },
            )
            app_module.db.session.commit()

    def create_category(self, name=None):
        payload = {
            'name': name or f'Category-{uuid.uuid4().hex[:8]}',
            'description': 'Mock category',
        }
        response = self.client.post('/api/categories', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_warehouse(self, name=None, capacity=1000):
        payload = {
            'name': name or f'Warehouse-{uuid.uuid4().hex[:8]}',
            'code': '',
            'address': 'Mock address',
            'capacity': capacity,
            'remarks': 'Mock warehouse',
        }
        response = self.client.post('/api/warehouses', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_item(self, category_id, name=None, minimum_stock=2, max_stock=25):
        payload = {
            'name': name or f'Item-{uuid.uuid4().hex[:8]}',
            'unit': 'Piece',
            'category_id': category_id,
            'minimum_stock': minimum_stock,
            'max_stock': max_stock,
            'storage_life_days': 365,
            'expiry_tracking': True,
            'batch_tracking': True,
            'serial_tracking': False,
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
            'description': 'Mock incident',
            'coordinates': '28.5,81.5',
            'affected_households': 200,
        }
        response = self.client.post('/api/incidents', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_beneficiary(self, name=None, national_id=None, ward=1, phone='9800000000', tole='Mock Tole'):
        payload = {
            'name': name or f'Beneficiary-{uuid.uuid4().hex[:8]}',
            'national_id': national_id or f'ID-{uuid.uuid4().hex[:8]}',
            'father_name': 'Mock Father',
            'phone': phone,
            'ward': ward,
            'tole': tole,
            'family_members': 4,
            'address': 'Mock Address',
        }
        response = self.client.post('/api/beneficiaries', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_fund(self, name=None, allocated_amount=1000):
        payload = {
            'name': name or f'Fund-{uuid.uuid4().hex[:8]}',
            'fiscal_year': '2081/82',
            'funding_source': 'Municipality',
            'allocated_amount': allocated_amount,
        }
        response = self.client.post('/api/cash-funds', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_receipt(self, warehouse_id, item_id, quantity=10):
        response = self.client.post(
            '/api/stock-receipts',
            json={
                'warehouse_id': warehouse_id,
                'source_type': 'Donation',
                'source_name': 'Mock Donor',
                'date': '2082-03-01',
                'items': [
                    {
                        'item_id': item_id,
                        'quantity': quantity,
                        'unit': 'Piece',
                        'unit_cost': 12.5,
                        'mfg_date': '2081-09-01',
                        'expiry_date': '2083-09-01',
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def test_login_page_and_redirect_guards(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

        response = self.client.get('/api/inventory')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['message'], 'Authentication required')

    def test_admin_login_logout_and_safe_next_redirect(self):
        response = self.login()
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

        response = self.login()
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            '/login?next=http://evil.example.com',
            data={'username': 'admin', 'password': 'admin123'},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('evil.example.com', response.headers['Location'])

    def test_invalid_login_and_locked_account(self):
        response = self.client.post(
            '/login',
            data={'username': 'admin', 'password': 'wrong-password'},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)

        with app_module.app.app_context():
            app_module.db.session.execute(
                app_module.db.text('UPDATE "user" SET locked_until = :locked_until WHERE username = :username'),
                {
                    'locked_until': datetime.now(timezone.utc) + timedelta(minutes=15),
                    'username': 'admin',
                },
            )
            app_module.db.session.commit()

        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Account locked', response.get_data(as_text=True))

    def test_user_management_permissions(self):
        self.create_user('editor1', password='editor123', role='editor', full_name='Editor One')

        response = self.login('editor1', 'editor123')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()['message'], 'Insufficient permissions')

        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)

        self.client.post('/logout', follow_redirects=False)

        response = self.login()
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['success'])
        self.assertTrue(any(user['username'] == 'admin' for user in payload['users']))

    def test_user_creation_validations(self):
        self.login()

        response = self.client.post('/api/users', json={'username': 'a', 'password': '123', 'role': 'viewer'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('at least 6 characters', response.get_json()['message'])

        response = self.client.post(
            '/api/users',
            json={'username': 'mock-user', 'password': 'password123', 'role': 'not-a-role'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Invalid role')

        response = self.client.post(
            '/api/users',
            json={'username': 'mock-user', 'password': 'password123', 'role': 'viewer', 'full_name': 'Mock User'},
        )
        self.assertEqual(response.status_code, 201)

        duplicate = self.client.post(
            '/api/users',
            json={'username': 'mock-user', 'password': 'password123', 'role': 'viewer'},
        )
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.get_json()['message'], 'Username already exists')

    def test_change_password_validates_inputs_and_updates_credentials(self):
        self.login()

        response = self.client.post('/api/auth/change-password', json={'old_password': 'admin123', 'new_password': '123'})
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/auth/change-password', json={'old_password': 'wrong', 'new_password': 'newpass123'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()['message'], 'Current password is incorrect')

        response = self.client.post('/api/auth/change-password', json={'old_password': 'admin123', 'new_password': 'newpass123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], 'Password changed successfully')

        self.client.post('/logout', follow_redirects=False)
        response = self.login('admin', 'newpass123')
        self.assertEqual(response.status_code, 302)

    def test_validation_helpers(self):
        self.assertTrue(app_module.validate_phone('9800000000'))
        self.assertTrue(app_module.validate_phone('+977 98-0000-0000'))
        self.assertFalse(app_module.validate_phone('bad-phone-number'))

        self.assertTrue(app_module.is_valid_nepali_date('2082-01-01'))
        self.assertFalse(app_module.is_valid_nepali_date('2082-13-01'))
        self.assertFalse(app_module.is_valid_nepali_date('2026/01/01'))

        self.assertEqual(app_module.parse_int_field({'count': '7'}, 'count', minimum=1), 7)
        self.assertEqual(app_module.parse_float_field({'amount': '12.5'}, 'amount', minimum=0), 12.5)
        self.assertTrue(app_module.parse_bool_field({'enabled': 'yes'}, 'enabled'))
        self.assertFalse(app_module.parse_bool_field({'enabled': 'off'}, 'enabled'))
        self.assertEqual(app_module.parse_date_field({'date': '2026-06-23'}, 'date').isoformat(), '2026-06-23')
        self.assertEqual(app_module.parse_bs_date_field({'date': '2082-01-01'}, 'date').isoformat(), '2025-04-14')

        with self.assertRaises(ValueError):
            app_module.parse_int_field({'count': 'x'}, 'count')
        with self.assertRaises(ValueError):
            app_module.parse_float_field({'amount': 'x'}, 'amount')
        with self.assertRaises(ValueError):
            app_module.parse_date_field({'date': '2026/06/23'}, 'date')
        with self.assertRaises(ValueError):
            app_module.parse_bs_date_field({'date': '2082-13-01'}, 'date')

    def test_smoke_end_to_end_inventory_flow(self):
        self.login()

        category = self.create_category()
        warehouse = self.create_warehouse()
        item = self.create_item(category['id'])
        self.create_receipt(warehouse['id'], item['id'], quantity=7)

        inventory = self.client.get(f'/api/inventory?warehouse_id={warehouse["id"]}&search={item["name"]}')
        self.assertEqual(inventory.status_code, 200)
        rows = inventory.get_json()['inventory']
        self.assertTrue(rows)
        self.assertEqual(rows[0]['item_name'], item['name'])
        self.assertEqual(rows[0]['quantity'], 7)

    def test_category_warehouse_supplier_validations(self):
        self.login()

        response = self.client.post('/api/categories', json={'name': '', 'description': 'x'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Category name is required')

        category = self.create_category()
        dup_category = self.client.post('/api/categories', json={'name': category['name'], 'description': 'dup'})
        self.assertEqual(dup_category.status_code, 500)

        response = self.client.post('/api/warehouses', json={'name': 'Bad Warehouse', 'code': '', 'phone': 'bad', 'capacity': 1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Phone number format is invalid')

        warehouse = self.create_warehouse()
        response = self.client.post(
            '/api/suppliers',
            json={'name': 'Supplier One', 'phone': 'bad-phone', 'email': 'supplier@example.com'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Phone number format is invalid')

        response = self.client.post(
            '/api/suppliers',
            json={'name': 'Supplier One', 'phone': '9800000001', 'email': 'bad-email'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Email format is invalid')

        supplier = self.client.post(
            '/api/suppliers',
            json={
                'name': 'Supplier One',
                'phone': '9800000001',
                'email': 'supplier@example.com',
                'address': 'Supplier Address',
            },
        )
        self.assertEqual(supplier.status_code, 201, supplier.get_json())

        duplicate_supplier = self.client.post(
            '/api/suppliers',
            json={'name': 'Supplier Two', 'phone': '9800000001', 'email': 'supplier2@example.com'},
        )
        self.assertEqual(duplicate_supplier.status_code, 400)

        with app_module.app.app_context():
            self.assertIsNotNone(app_module.db.session.get(app_module.Warehouse, warehouse['id']))

    def test_incident_distribution_workflow(self):
        self.login()

        category = self.create_category()
        warehouse = self.create_warehouse()
        item = self.create_item(category['id'])
        incident = self.create_incident(ward=1)
        self.create_receipt(warehouse['id'], item['id'], quantity=10)

        bad_incident = self.client.post(
            '/api/incidents',
            json={'incident_name': 'Invalid ward case', 'incident_type': 'Flood', 'ward': 99, 'coordinates': '28.5,81.5'},
        )
        self.assertEqual(bad_incident.status_code, 400)
        self.assertEqual(bad_incident.get_json()['message'], 'Invalid ward selected')

        invalid_distribution = self.client.post(
            '/api/distributions',
            json={
                'warehouse_id': warehouse['id'],
                'incident_id': incident['id'],
                'destination': 'Mock Destination',
                'receiver': 'Mock Receiver',
                'phone': '9800000000',
                'distribution_date': '2099-01-01',
                'items': [{'item_id': item['id'], 'warehouse_id': warehouse['id'], 'quantity': 4, 'unit': 'Piece'}],
                'beneficiaries': [{'family_name': 'Family A', 'members': 3, 'item': None, 'quantity': 4}],
            },
        )
        self.assertEqual(invalid_distribution.status_code, 400)
        self.assertEqual(invalid_distribution.get_json()['message'], 'Distribution date cannot be in the future')

        distribution = self.client.post(
            '/api/distributions',
            json={
                'warehouse_id': warehouse['id'],
                'incident_id': incident['id'],
                'destination': 'Mock Destination',
                'receiver': 'Mock Receiver',
                'phone': '9800000000',
                'distribution_date': '2082-03-02',
                'items': [{'item_id': item['id'], 'warehouse_id': warehouse['id'], 'quantity': 4, 'unit': 'Piece'}],
                'beneficiaries': [{'family_name': 'Family A', 'members': 3, 'item': None, 'quantity': 4}],
            },
        )
        self.assertEqual(distribution.status_code, 201, distribution.get_json())
        distribution_data = distribution.get_json()['data']

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=warehouse['id']).first()
            self.assertEqual(inv.quantity, 6)
            dist_model = app_module.db.session.get(app_module.Distribution, distribution_data['id'])
            self.assertEqual(dist_model.status, 'Completed')
            di = app_module.DistributionItem.query.filter_by(distribution_id=dist_model.id).first()
            self.assertEqual(di.quantity, 4)

        # A second distribution exceeding remaining stock is rejected
        duplicate_distribution = self.client.post(
            '/api/distributions',
            json={
                'warehouse_id': warehouse['id'],
                'incident_id': incident['id'],
                'destination': 'Mock Destination',
                'receiver': 'Mock Receiver',
                'phone': '9800000000',
                'distribution_date': '2082-03-04',
                'items': [{'item_id': item['id'], 'warehouse_id': warehouse['id'], 'quantity': 7, 'unit': 'Piece'}],
                'beneficiaries': [
                    {'family_name': 'Family B', 'members': 3, 'item': None, 'quantity': 7},
                ],
            },
        )
        self.assertEqual(duplicate_distribution.status_code, 400)

    def test_cash_and_beneficiary_workflows(self):
        self.login()

        beneficiary = self.create_beneficiary()
        duplicate_beneficiary = self.client.post(
            '/api/beneficiaries',
            json={
                'name': 'Other Name',
                'national_id': beneficiary['national_id'],
                'phone': beneficiary['phone'],
                'ward': beneficiary['ward'],
                'tole': 'Other Tole',
            },
        )
        self.assertEqual(duplicate_beneficiary.status_code, 400)

        incident = self.create_incident(name=f'Cash-{uuid.uuid4().hex[:8]}', incident_type='Fire', ward=2)
        fund = self.create_fund()

        bad_receipt = self.client.post(
            '/api/cash-receipts',
            json={'fund_id': fund['id'], 'receipt_date': '2082-03-01'},
        )
        self.assertEqual(bad_receipt.status_code, 400)
        self.assertIn('Amount received is required', bad_receipt.get_json()['message'])

        receipt = self.client.post(
            '/api/cash-receipts',
            json={
                'fund_id': fund['id'],
                'receipt_date': '2082-03-01',
                'amount_received': 500,
                'funding_source': 'Donation',
            },
        )
        self.assertEqual(receipt.status_code, 201, receipt.get_json())

        request = self.client.post(
            '/api/cash-requests',
            json={
                'incident_id': incident['id'],
                'requesting_office': 'Mock Office',
                'requester_name': 'Mock Requester',
                'phone': '9800000000',
                'priority': 'High',
                'requested_amount': 300,
                'purpose': 'Emergency assistance',
                'remarks': 'Cash request',
                'request_date': '2082-03-01',
                'beneficiary_id': beneficiary['id'],
            },
        )
        self.assertEqual(request.status_code, 201, request.get_json())
        request_data = request.get_json()['data']

        distribution = self.client.post(
            '/api/cash-distributions',
            json={
                'fund_id': fund['id'],
                'incident_id': incident['id'],
                'cash_request_id': request_data['id'],
                'distribution_type': 'Individual',
                'distribution_date': '2082-03-03',
                'officer': 'Mock Officer',
                'remarks': 'Mock cash distribution',
                'beneficiaries': [
                    {'name': 'Cash Family A', 'national_id': 'N-1', 'amount': 100, 'beneficiary_id': beneficiary['id']},
                    {'name': 'Cash Family B', 'national_id': 'N-2', 'amount': 200},
                ],
            },
        )
        self.assertEqual(distribution.status_code, 201, distribution.get_json())

        with app_module.app.app_context():
            fund_row = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(fund_row.current_balance, 200)
            cash_req = app_module.db.session.get(app_module.CashRequest, request_data['id'])
            self.assertEqual(cash_req.status, 'Completed')

        cash_dist_id = distribution.get_json()['data']['id']
        response = self.client.get(f'/api/cash-distributions/{cash_dist_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['distribution']['total_amount'], 300)

        history = self.client.get(f'/api/beneficiaries/{beneficiary["id"]}/history')
        self.assertEqual(history.status_code, 200)
        self.assertTrue(history.get_json()['success'])

    def test_stock_transfer_and_adjustment_workflows(self):
        self.login()

        category = self.create_category()
        source_wh = self.create_warehouse(name=f'Source-{uuid.uuid4().hex[:6]}')
        dest_wh = self.create_warehouse(name=f'Dest-{uuid.uuid4().hex[:6]}')
        item = self.create_item(category['id'])
        self.create_receipt(source_wh['id'], item['id'], quantity=8)

        same_warehouse = self.client.post(
            '/api/stock-transfers',
            json={
                'from_warehouse_id': source_wh['id'],
                'to_warehouse_id': source_wh['id'],
                'transfer_date': '2082-03-01',
                'items': [{'item_id': item['id'], 'quantity': 2, 'unit': 'Piece'}],
            },
        )
        self.assertEqual(same_warehouse.status_code, 400)
        self.assertEqual(same_warehouse.get_json()['message'], 'Source and destination warehouses must be different')

        transfer = self.client.post(
            '/api/stock-transfers',
            json={
                'from_warehouse_id': source_wh['id'],
                'to_warehouse_id': dest_wh['id'],
                'transfer_date': '2082-03-01',
                'items': [{'item_id': item['id'], 'quantity': 3, 'unit': 'Piece'}],
            },
        )
        self.assertEqual(transfer.status_code, 201, transfer.get_json())

        with app_module.app.app_context():
            source_inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=source_wh['id']).first()
            dest_inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=dest_wh['id']).first()
            self.assertEqual(source_inv.quantity, 5)
            self.assertEqual(dest_inv.quantity, 3)

        bad_adjustment = self.client.post(
            '/api/adjustments',
            json={
                'item_id': item['id'],
                'warehouse_id': source_wh['id'],
                'adjustment_type': 'BadType',
                'adjusted_quantity': 1,
            },
        )
        self.assertEqual(bad_adjustment.status_code, 400)
        self.assertEqual(bad_adjustment.get_json()['message'], 'Invalid adjustment type')

        adjustment = self.client.post(
            '/api/adjustments',
            json={
                'item_id': item['id'],
                'warehouse_id': source_wh['id'],
                'adjustment_type': 'Decrease',
                'adjusted_quantity': 2,
                'reason': 'Damage',
                'remarks': 'Mock adjustment',
                'date': '2082-03-04',
            },
        )
        self.assertEqual(adjustment.status_code, 201, adjustment.get_json())

        with app_module.app.app_context():
            source_inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=source_wh['id']).first()
            self.assertEqual(source_inv.quantity, 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
