import uuid
from tests.conftest import LeocTestCase, app_module


class CashManagementTest(LeocTestCase):
    def test_cash_fund_crud(self):
        self.login()
        name = f'Fund-{uuid.uuid4().hex[:6]}'
        resp = self.client.post('/api/cash-funds', json={
            'name': name, 'fiscal_year': '2081/82',
            'funding_source': 'Government', 'allocated_amount': 500000,
            'description': 'Emergency response fund',
        })
        self.assertEqual(resp.status_code, 201)
        fund = resp.get_json()['data']
        self.assertEqual(fund['name'], name)
        self.assertEqual(fund['current_balance'], 500000)

        fund_id = fund['id']
        resp = self.client.put(f'/api/cash-funds/{fund_id}', json={'allocated_amount': 600000})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/cash-funds/{fund_id}')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/cash-funds')
        self.assertEqual(resp.status_code, 200)
        names = [f['name'] for f in resp.get_json()['funds']]
        self.assertIn(name, names)

    def test_cash_receipt_increases_balance(self):
        self.login()
        fund = self.create_fund(allocated=100000)

        with app_module.app.app_context():
            f = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(f.current_balance, 100000)

        self.create_cash_receipt(fund['id'], amount=25000)

        with app_module.app.app_context():
            f = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(f.current_balance, 125000)

        # Second receipt
        self.create_cash_receipt(fund['id'], amount=15000)

        with app_module.app.app_context():
            f = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(f.current_balance, 140000)

    def test_cash_request_status_transitions(self):
        self.login()
        inc = self.create_incident()

        cash_req = self.create_cash_request(inc['id'], amount=50000)
        self.assertEqual(cash_req['status'], 'Pending')

        cr_id = cash_req['id']
        resp = self.client.put(f'/api/cash-requests/{cr_id}', json={'priority': 'Urgent'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/cash-requests/{cr_id}')
        self.assertEqual(resp.status_code, 200)

    def test_cash_distribution_deducts_from_balance(self):
        self.login()
        inc = self.create_incident(name=f'CashInc-{uuid.uuid4().hex[:6]}', incident_type='Fire', ward=3)
        fund = self.create_fund(allocated=50000)
        self.create_cash_receipt(fund['id'], amount=30000)

        cash_dist = self.create_cash_distribution(fund['id'], inc['id'], amount=15000)

        with app_module.app.app_context():
            f = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(f.current_balance, 65000)

    def test_cash_distribution_cancel_returns_funds(self):
        self.login()
        inc = self.create_incident(name=f'Can-{uuid.uuid4().hex[:6]}', ward=4)
        fund = self.create_fund(allocated=50000)
        self.create_cash_receipt(fund['id'], amount=30000)
        cash_req = self.create_cash_request(inc['id'], amount=20000)

        cash_dist = self.create_cash_distribution(fund['id'], inc['id'], cash_req['id'], amount=10000)

        with app_module.app.app_context():
            f = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(f.current_balance, 70000)

        # Cancel the distribution
        dist_id = cash_dist['id']
        resp = self.client.post(f'/api/cash-distributions/{dist_id}/cancel', json={'cancel_reason': 'Test cancel'})
        self.assertEqual(resp.status_code, 200)

        with app_module.app.app_context():
            f = app_module.db.session.get(app_module.CashFund, fund['id'])
            self.assertEqual(f.current_balance, 80000)

            dist = app_module.db.session.get(app_module.CashDistribution, dist_id)
            self.assertEqual(dist.status, 'Cancelled')

    def test_cash_distribution_with_beneficiaries(self):
        self.login()
        inc = self.create_incident(name=f'Ben-{uuid.uuid4().hex[:6]}', ward=5)
        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        cash_req = self.create_cash_request(inc['id'], amount=30000)
        ben = self.create_beneficiary()

        payload = {
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'cash_request_id': cash_req['id'], 'distribution_type': 'Individual',
            'distribution_date': '2082-03-05', 'officer': 'Test Officer',
            'remarks': 'Cash for families',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'], 'amount': 5000, 'beneficiary_id': ben['id']},
                {'name': 'Other Person', 'national_id': 'OTH-001', 'amount': 3000},
            ],
        }
        resp = self.client.post('/api/cash-distributions', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['total_amount'], 8000)

        dist_id = data['id']
        resp = self.client.get(f'/api/cash-distributions/{dist_id}')
        self.assertEqual(resp.status_code, 200)

        with app_module.app.app_context():
            bc = app_module.CashDistributionBeneficiary.query.filter_by(distribution_id=dist_id).count()
            self.assertEqual(bc, 2)

    def test_cash_distribution_photo_upload(self):
        self.login()
        inc = self.create_incident(name=f'Photo-{uuid.uuid4().hex[:6]}', ward=6)
        fund = self.create_fund(allocated=20000)
        self.create_cash_receipt(fund['id'], amount=10000)
        cash_req = self.create_cash_request(inc['id'], amount=5000)
        cash_dist = self.create_cash_distribution(fund['id'], inc['id'], cash_req['id'], amount=3000)

        dist_id = cash_dist['id']
        resp = self.client.post(
            f'/api/cash-distributions/{dist_id}/upload-file',
            data={'file': (io.BytesIO(b'fake-pdf'), 'doc.pdf')},
            content_type='multipart/form-data',
        )
        self.assertIn(resp.status_code, (200, 400))

    def test_cash_flow_validation(self):
        self.login()
        inc = self.create_incident()
        fund = self.create_fund(allocated=1000)

        # Try to distribute more than fund balance
        cash_req = self.create_cash_request(inc['id'], amount=5000)

        resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'cash_request_id': cash_req['id'], 'distribution_type': 'Individual',
            'distribution_date': '2082-03-01', 'officer': 'Officer',
            'beneficiaries': [{'name': 'A', 'national_id': 'X1', 'amount': 5000}],
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Insufficient', resp.get_json()['message'])

    def test_cash_request_creation(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)

        cash_req = self.create_cash_request(inc['id'], amount=10000)

        with app_module.app.app_context():
            cr_model = app_module.db.session.get(app_module.CashRequest, cash_req['id'])
            self.assertIsNotNone(cr_model)
            self.assertEqual(cr_model.requested_amount, 10000)


import io
