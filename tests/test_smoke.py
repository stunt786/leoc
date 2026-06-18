import os
import tempfile
import unittest
import uuid


_db_fd, _db_path = tempfile.mkstemp(prefix='leoc_smoke_', suffix='.sqlite')
os.close(_db_fd)
os.environ.setdefault('SECRET_KEY', 'smoke-test-secret')
os.environ.setdefault('ADMIN_PASSWORD', 'admin123')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'

import app as app_module


class SmokeTestCase(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        with app_module.app.app_context():
            app_module.db.session.remove()
            app_module.db.engine.dispose()
        try:
            os.remove(_db_path)
        except FileNotFoundError:
            pass

    def make_client(self):
        app_module.app.config['TESTING'] = True
        return app_module.app.test_client()

    def login_admin(self):
        client = self.make_client()
        response = client.post(
            '/login',
            data={'username': 'admin', 'password': 'admin123'},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        return client

    def create_category(self, client, name=None):
        payload = {
            'name': name or f'Category-{uuid.uuid4().hex[:8]}',
            'description': 'Smoke test category',
        }
        response = client.post('/api/categories', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_warehouse(self, client, name=None):
        payload = {
            'name': name or f'Warehouse-{uuid.uuid4().hex[:8]}',
            'code': '',
            'address': 'Smoke test address',
            'capacity': 1000,
            'remarks': 'Smoke test warehouse',
        }
        response = client.post('/api/warehouses', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_item(self, client, category_id, name=None):
        payload = {
            'name': name or f'Item-{uuid.uuid4().hex[:8]}',
            'unit': 'Piece',
            'category_id': category_id,
            'minimum_stock': 2,
            'max_stock': 25,
            'storage_life_days': 365,
            'expiry_tracking': True,
            'batch_tracking': True,
            'serial_tracking': False,
            'is_consumable': True,
            'storage_requirement': 'Normal',
        }
        response = client.post('/api/items', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_incident(self, client, name=None, incident_type='Flood', ward=1):
        payload = {
            'incident_name': name or f'Incident-{uuid.uuid4().hex[:8]}',
            'incident_type': incident_type,
            'ward': ward,
            'start_date': '2082-01-01',
            'status': 'Active',
            'description': 'Smoke test incident',
        }
        response = client.post('/api/incidents', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def create_relief_request(self, client, incident_id, item_id, quantity_requested=4):
        payload = {
            'incident_id': incident_id,
            'organization': 'Smoke Relief Org',
            'requester_name': 'Smoke Requester',
            'phone': '9800000000',
            'priority': 'High',
            'requested_cash_amount': 0,
            'cash_purpose': 'Smoke test',
            'remarks': 'Smoke test relief request',
            'items': [
                {
                    'item_id': item_id,
                    'quantity_requested': quantity_requested,
                    'unit': 'Piece',
                }
            ],
        }
        response = client.post('/api/relief-requests', json=payload)
        self.assertEqual(response.status_code, 201, response.get_json())
        return response.get_json()['data']

    def test_anonymous_inventory_requires_login(self):
        client = self.make_client()
        response = client.get('/api/inventory')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['message'], 'Authentication required')

    def test_stock_receipt_updates_inventory(self):
        client = self.login_admin()
        category = self.create_category(client)
        warehouse = self.create_warehouse(client)
        item = self.create_item(client, category['id'])

        receipt_payload = {
            'warehouse_id': warehouse['id'],
            'source_type': 'Donation',
            'source_name': 'Smoke Test Donor',
            'date': '2082-03-01',
            'items': [
                {
                    'item_id': item['id'],
                    'quantity': 7,
                    'unit': 'Piece',
                    'unit_cost': 12.5,
                    'mfg_date': '2081-09-01',
                    'expiry_date': '2083-09-01',
                }
            ],
        }
        receipt_response = client.post('/api/stock-receipts', json=receipt_payload)
        self.assertEqual(receipt_response.status_code, 201, receipt_response.get_json())

        inventory_response = client.get(f"/api/inventory?warehouse_id={warehouse['id']}&search={item['name']}")
        self.assertEqual(inventory_response.status_code, 200, inventory_response.get_json())
        inventory_items = inventory_response.get_json()['inventory']
        self.assertTrue(inventory_items, 'Expected at least one inventory row')
        self.assertEqual(inventory_items[0]['item_name'], item['name'])
        self.assertEqual(inventory_items[0]['quantity'], 7)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(
                item_id=item['id'],
                warehouse_id=warehouse['id'],
            ).first()
            self.assertIsNotNone(inv)
            self.assertEqual(inv.quantity, 7)

    def test_validation_smoke_paths(self):
        client = self.login_admin()
        category = self.create_category(client)
        warehouse = self.create_warehouse(client)
        item = self.create_item(client, category['id'])

        bad_incident = client.post(
            '/api/incidents',
            json={
                'incident_name': 'Flood Event',
                'incident_type': 'Flood',
                'ward': 99,
            },
        )
        self.assertEqual(bad_incident.status_code, 400)
        self.assertIn('Ward must be between 1 and 9', bad_incident.get_json()['message'])

        bad_item = client.post(
            '/api/items',
            json={
                'name': 'Bad Item',
                'unit': 'Piece',
                'category_id': 999999,
            },
        )
        self.assertEqual(bad_item.status_code, 404)
        self.assertIn('Category not found', bad_item.get_json()['message'])

        fund_response = client.post(
            '/api/cash-funds',
            json={
                'name': f'Fund-{uuid.uuid4().hex[:8]}',
                'fiscal_year': '2081/82',
                'funding_source': 'Municipality',
                'allocated_amount': 1000,
            },
        )
        self.assertEqual(fund_response.status_code, 201, fund_response.get_json())
        fund = fund_response.get_json()['data']

        bad_cash_receipt = client.post(
            '/api/cash-receipts',
            json={
                'fund_id': fund['id'],
                'receipt_date': '2082-03-01',
            },
        )
        self.assertEqual(bad_cash_receipt.status_code, 400)
        self.assertIn('Amount received is required', bad_cash_receipt.get_json()['message'])

    def test_material_flow_smoke(self):
        client = self.login_admin()
        category = self.create_category(client)
        warehouse = self.create_warehouse(client)
        item = self.create_item(client, category['id'])
        incident = self.create_incident(client)

        receipt_response = client.post(
            '/api/stock-receipts',
            json={
                'warehouse_id': warehouse['id'],
                'source_type': 'Donation',
                'source_name': 'Smoke Test Donor',
                'date': '2082-03-01',
                'items': [
                    {
                        'item_id': item['id'],
                        'quantity': 10,
                        'unit': 'Piece',
                        'unit_cost': 12.5,
                        'mfg_date': '2081-09-01',
                        'expiry_date': '2083-09-01',
                    }
                ],
            },
        )
        self.assertEqual(receipt_response.status_code, 201, receipt_response.get_json())

        relief_request = self.create_relief_request(client, incident['id'], item['id'], quantity_requested=4)
        dispatch_response = client.post(
            '/api/dispatch',
            json={
                'warehouse_id': warehouse['id'],
                'incident_id': incident['id'],
                'relief_request_id': relief_request['id'],
                'destination': 'Smoke Test Destination',
                'receiver': 'Smoke Receiver',
                'phone': '9800000000',
                'date': '2082-03-02',
                'items': [
                    {
                        'item_id': item['id'],
                        'quantity': 4,
                        'unit': 'Piece',
                        'batch_no': 'BATCH-001',
                        'expiry_date': '2083-09-01',
                    }
                ],
            },
        )
        self.assertEqual(dispatch_response.status_code, 201, dispatch_response.get_json())
        dispatch = dispatch_response.get_json()['data']

        distribution_response = client.post(
            '/api/distributions',
            json={
                'dispatch_id': dispatch['id'],
                'location': 'Ward 1',
                'distribution_date': '2082-03-03',
                'officer': 'Smoke Officer',
                'remarks': 'Smoke distribution',
                'beneficiaries': [
                    {'family_name': 'Family A', 'members': 3, 'item': item['name'], 'quantity': 2},
                    {'family_name': 'Family B', 'members': 4, 'item': item['name'], 'quantity': 2},
                ],
            },
        )
        self.assertEqual(distribution_response.status_code, 201, distribution_response.get_json())

        with app_module.app.app_context():
            req = app_module.db.session.get(app_module.ReliefRequest, relief_request['id'])
            self.assertIsNotNone(req)
            self.assertEqual(req.status, 'Completed')
            inv = app_module.Inventory.query.filter_by(
                item_id=item['id'],
                warehouse_id=warehouse['id'],
            ).first()
            self.assertIsNotNone(inv)
            self.assertEqual(inv.quantity, 6)

    def test_cash_flow_smoke(self):
        client = self.login_admin()
        incident = self.create_incident(client, name=f'CashIncident-{uuid.uuid4().hex[:8]}', incident_type='Fire', ward=2)

        fund_response = client.post(
            '/api/cash-funds',
            json={
                'name': f'Fund-{uuid.uuid4().hex[:8]}',
                'fiscal_year': '2081/82',
                'funding_source': 'Municipality',
                'allocated_amount': 1000,
            },
        )
        self.assertEqual(fund_response.status_code, 201, fund_response.get_json())
        fund = fund_response.get_json()['data']

        cash_request_response = client.post(
            '/api/cash-requests',
            json={
                'incident_id': incident['id'],
                'requesting_office': 'Smoke Office',
                'requester_name': 'Smoke Requester',
                'phone': '9800000000',
                'priority': 'High',
                'requested_amount': 300,
                'purpose': 'Smoke cash support',
                'remarks': 'Smoke cash request',
                'request_date': '2082-03-01',
            },
        )
        self.assertEqual(cash_request_response.status_code, 201, cash_request_response.get_json())
        cash_request = cash_request_response.get_json()['data']

        cash_distribution_response = client.post(
            '/api/cash-distributions',
            json={
                'fund_id': fund['id'],
                'incident_id': incident['id'],
                'cash_request_id': cash_request['id'],
                'distribution_type': 'Individual',
                'distribution_date': '2082-03-03',
                'officer': 'Smoke Officer',
                'remarks': 'Smoke cash distribution',
                'beneficiaries': [
                    {'name': 'Beneficiary A', 'national_id': 'A-1', 'amount': 100},
                    {'name': 'Beneficiary B', 'national_id': 'B-1', 'amount': 200},
                ],
            },
        )
        self.assertEqual(cash_distribution_response.status_code, 201, cash_distribution_response.get_json())

        with app_module.app.app_context():
            req = app_module.db.session.get(app_module.CashRequest, cash_request['id'])
            self.assertIsNotNone(req)
            self.assertEqual(req.status, 'Completed')
            fund_row = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertIsNotNone(fund_row)
            self.assertEqual(fund_row.current_balance, 700)
            dist_count = app_module.CashDistribution.query.filter_by(
                cash_request_id=cash_request['id'],
                fund_id=fund['id'],
            ).count()
            self.assertEqual(dist_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
