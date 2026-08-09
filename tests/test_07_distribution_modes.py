import uuid
from tests.conftest import LeocTestCase, app_module


def set_distribution_mode(mode):
    with app_module.app.app_context():
        app_module.AppSettings.set_setting('distribution_mode', mode)


def set_distribution_repetitions(n):
    with app_module.app.app_context():
        app_module.AppSettings.set_setting('distribution_repetitions', n)


class DistributionModeTest(LeocTestCase):
    def setUp(self):
        super().setUp()
        self.login()
        set_distribution_mode('')
        set_distribution_repetitions(1)

    def test_default_mode_allows_both(self):
        with app_module.app.app_context():
            self.assertEqual(app_module.get_distribution_mode('2081/82'), 'cash_and_items')

    def test_settings_api_roundtrip(self):
        resp = self.client.post('/api/settings/distribution_mode', json={'value': 'cash_only'})
        self.assertEqual(resp.status_code, 200, resp.get_json())
        resp = self.client.get('/api/settings/distribution_mode')
        self.assertEqual(resp.status_code, 200, resp.get_json())
        self.assertEqual(resp.get_json()['value'], 'cash_only')

    def test_cash_blocked_in_items_only_mode(self):
        set_distribution_mode('items_only')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=2)
        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        ben = self.create_beneficiary()
        resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(resp.status_code, 400, resp.get_json())
        self.assertIn('Cash distribution is not allowed', resp.get_json()['message'])

    def test_items_blocked_in_cash_only_mode(self):
        set_distribution_mode('cash_only')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=2)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        resp = self.client.post('/api/distributions', json={
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4,
                       'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': 'Family A', 'members': 3, 'item': None, 'quantity': 2},
            ],
        })
        self.assertEqual(resp.status_code, 400, resp.get_json())
        self.assertIn('Relief item distribution is not allowed', resp.get_json()['message'])

    def test_cash_allowed_in_cash_only_mode(self):
        set_distribution_mode('cash_only')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=3)
        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        ben = self.create_beneficiary()
        resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(resp.status_code, 201, resp.get_json())

    def test_items_allowed_in_items_only_mode(self):
        set_distribution_mode('items_only')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=3)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        resp = self.client.post('/api/distributions', json={
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4,
                       'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': 'Family A', 'members': 3, 'item': None, 'quantity': 2},
            ],
        })
        self.assertEqual(resp.status_code, 201, resp.get_json())

    def test_items_then_cash_blocked_in_items_only_mode(self):
        set_distribution_mode('items_only')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=4)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)

        items_resp = self.client.post('/api/distributions', json={
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4,
                       'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': 'Family A', 'members': 3, 'item': None, 'quantity': 2},
            ],
        })
        self.assertEqual(items_resp.status_code, 201, items_resp.get_json())

        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        cash_resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': 'Family A', 'amount': 5000},
            ],
        })
        self.assertEqual(cash_resp.status_code, 400, cash_resp.get_json())
        self.assertIn('Cash distribution is not allowed', cash_resp.get_json()['message'])

    def test_cash_blocked_after_items_for_same_incident(self):
        set_distribution_mode('cash_and_items')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=4)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        ben = self.create_beneficiary()

        items_resp = self.client.post('/api/distributions', json={
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4,
                       'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
                 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(items_resp.status_code, 201, items_resp.get_json())

        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        cash_resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(cash_resp.status_code, 400, cash_resp.get_json())
        self.assertIn('only ONE distribution per incident', cash_resp.get_json()['message'])

    def test_combined_cash_plus_items_linked_distribution_allowed(self):
        set_distribution_mode('cash_and_items')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=4)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        ben = self.create_beneficiary()

        items_resp = self.client.post('/api/distributions', json={
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4,
                       'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
                 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(items_resp.status_code, 201, items_resp.get_json())
        dist_id = items_resp.get_json()['data']['id']

        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        cash_resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'distribution_id': dist_id,
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(cash_resp.status_code, 201, cash_resp.get_json())

    def test_items_blocked_after_cash_for_same_incident(self):
        set_distribution_mode('cash_and_items')
        inc = self.create_incident(name=f'ModeInc-{uuid.uuid4().hex[:6]}', ward=5)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        ben = self.create_beneficiary()
        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)

        cash_resp = self.client.post('/api/cash-distributions', json={
            'fund_id': fund['id'], 'incident_id': inc['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(cash_resp.status_code, 201, cash_resp.get_json())

        items_resp = self.client.post('/api/distributions', json={
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4,
                       'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
                 'beneficiary_id': ben['id']},
            ],
        })
        self.assertEqual(items_resp.status_code, 400, items_resp.get_json())
        self.assertIn('only ONE distribution per incident', items_resp.get_json()['message'])

    def test_api_data_exposes_mode(self):
        set_distribution_mode('cash_only')
        resp = self.client.get('/api/data')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['distribution_mode'], 'cash_only')
        self.assertEqual(data['active_distribution_mode'], 'cash_only')

    # ============ DISTRIBUTION REPETITIONS ============

    def _items_payload(self, incident, item, warehouse):
        return {
            'incident_id': incident['id'],
            'warehouse_id': warehouse['id'],
            'distribution_date': '2082-03-03',
            'items': [{'item_id': item['id'], 'warehouse_id': warehouse['id'], 'quantity': 4,
                       'unit': 'Piece'}],
        }

    def _make_item_env(self, ward):
        inc = self.create_incident(name=f'RepInc-{uuid.uuid4().hex[:6]}', ward=ward)
        cat = self.create_category()
        item = self.create_item(cat['id'])
        wh = self.create_warehouse()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        return inc, item, wh

    def test_default_repetitions_is_once_only_for_items(self):
        set_distribution_repetitions(1)
        inc, item, wh = self._make_item_env(2)
        ben = self.create_beneficiary()
        payload = self._items_payload(inc, item, wh)
        payload['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        r1 = self.client.post('/api/distributions', json=payload)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        r2 = self.client.post('/api/distributions', json=payload)
        self.assertEqual(r2.status_code, 400, r2.get_json())
        self.assertIn('only ONE distribution per incident', r2.get_json()['message'])

    def test_repetitions_allows_two_items_distributions_for_different_incidents(self):
        set_distribution_repetitions(2)
        inc_a, item_a, wh_a = self._make_item_env(3)
        inc_b, item_b, wh_b = self._make_item_env(4)
        ben = self.create_beneficiary()
        payload_a = self._items_payload(inc_a, item_a, wh_a)
        payload_a['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        payload_b = self._items_payload(inc_b, item_b, wh_b)
        payload_b['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        r1 = self.client.post('/api/distributions', json=payload_a)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        r2 = self.client.post('/api/distributions', json=payload_b)
        self.assertEqual(r2.status_code, 201, r2.get_json())
        # Third incident should be blocked with reps=2
        inc_c, item_c, wh_c = self._make_item_env(5)
        payload_c = self._items_payload(inc_c, item_c, wh_c)
        payload_c['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        r3 = self.client.post('/api/distributions', json=payload_c)
        self.assertEqual(r3.status_code, 400, r3.get_json())
        self.assertIn('maximum of 2', r3.get_json()['message'])

    def test_repetitions_allows_two_cash_distributions_for_different_incidents(self):
        set_distribution_repetitions(2)
        inc_a = self.create_incident(name=f'RepInc-{uuid.uuid4().hex[:6]}', ward=4)
        inc_b = self.create_incident(name=f'RepInc-{uuid.uuid4().hex[:6]}', ward=5)
        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        ben = self.create_beneficiary()
        payload_a = {
            'fund_id': fund['id'], 'incident_id': inc_a['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        }
        payload_b = dict(payload_a, incident_id=inc_b['id'])
        r1 = self.client.post('/api/cash-distributions', json=payload_a)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        r2 = self.client.post('/api/cash-distributions', json=payload_b)
        self.assertEqual(r2.status_code, 201, r2.get_json())
        # Third incident should be blocked with reps=2
        inc_c = self.create_incident(name=f'RepInc-{uuid.uuid4().hex[:6]}', ward=6)
        payload_c = dict(payload_a, incident_id=inc_c['id'])
        r3 = self.client.post('/api/cash-distributions', json=payload_c)
        self.assertEqual(r3.status_code, 400, r3.get_json())
        self.assertIn('maximum of 2', r3.get_json()['message'])

    def test_repetitions_blocks_third_items_distribution(self):
        set_distribution_repetitions(3)
        inc_a, item_a, wh_a = self._make_item_env(5)
        inc_b, item_b, wh_b = self._make_item_env(6)
        inc_c, item_c, wh_c = self._make_item_env(7)
        ben = self.create_beneficiary()
        payload_a = self._items_payload(inc_a, item_a, wh_a)
        payload_a['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        payload_b = self._items_payload(inc_b, item_b, wh_b)
        payload_b['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        payload_c = self._items_payload(inc_c, item_c, wh_c)
        payload_c['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        for payload in [payload_a, payload_b, payload_c]:
            resp = self.client.post('/api/distributions', json=payload)
            self.assertEqual(resp.status_code, 201, resp.get_json())
        # Fourth incident should be blocked with reps=3
        inc_d, item_d, wh_d = self._make_item_env(8)
        payload_d = self._items_payload(inc_d, item_d, wh_d)
        payload_d['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        resp = self.client.post('/api/distributions', json=payload_d)
        self.assertEqual(resp.status_code, 400, resp.get_json())
        self.assertIn('maximum of 3', resp.get_json()['message'])

    def test_items_blocked_across_different_incidents_when_reps_is_one(self):
        set_distribution_repetitions(1)
        inc_a, item_a, wh_a = self._make_item_env(6)
        inc_b, item_b, wh_b = self._make_item_env(7)
        ben = self.create_beneficiary()
        payload_a = self._items_payload(inc_a, item_a, wh_a)
        payload_a['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        payload_b = self._items_payload(inc_b, item_b, wh_b)
        payload_b['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        r1 = self.client.post('/api/distributions', json=payload_a)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        r2 = self.client.post('/api/distributions', json=payload_b)
        self.assertEqual(r2.status_code, 400, r2.get_json())
        self.assertIn('maximum of 1', r2.get_json()['message'])

    def test_cash_blocked_across_different_incidents_when_reps_is_one(self):
        set_distribution_repetitions(1)
        inc_a = self.create_incident(name=f'RepInc-{uuid.uuid4().hex[:6]}', ward=8)
        inc_b = self.create_incident(name=f'RepInc-{uuid.uuid4().hex[:6]}', ward=9)
        fund = self.create_fund(allocated=100000)
        self.create_cash_receipt(fund['id'], amount=50000)
        ben = self.create_beneficiary()
        payload = {
            'fund_id': fund['id'], 'incident_id': inc_a['id'],
            'distribution_type': 'Individual',
            'distribution_date': '2082-03-05',
            'beneficiaries': [
                {'name': ben['name'], 'national_id': ben['national_id'],
                 'amount': 5000, 'beneficiary_id': ben['id']},
            ],
        }
        payload_b = dict(payload, incident_id=inc_b['id'])
        r1 = self.client.post('/api/cash-distributions', json=payload)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        r2 = self.client.post('/api/cash-distributions', json=payload_b)
        self.assertEqual(r2.status_code, 400, r2.get_json())
        self.assertIn('maximum of 1', r2.get_json()['message'])

    def test_same_incident_counts_distributions_not_items(self):
        set_distribution_repetitions(1)
        inc, item, wh = self._make_item_env(6)
        cat = self.create_category()
        item2 = self.create_item(cat['id'])
        self.create_stock_receipt(wh['id'], item2['id'], quantity=20)
        ben = self.create_beneficiary()
        payload = self._items_payload(inc, item, wh)
        payload['items'].append({'item_id': item2['id'], 'warehouse_id': wh['id'], 'quantity': 4, 'unit': 'Piece'})
        payload['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': item['name'], 'quantity': 2,
             'beneficiary_id': ben['id']},
            {'family_name': ben['name'], 'members': 3, 'item': item2['name'], 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        r1 = self.client.post('/api/distributions', json=payload)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        payload['items'] = payload['items'][:1]
        payload['beneficiaries'] = [
            {'family_name': ben['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben['id']},
        ]
        r2 = self.client.post('/api/distributions', json=payload)
        self.assertEqual(r2.status_code, 400, r2.get_json())
        self.assertIn('only ONE distribution per incident', r2.get_json()['message'])

    def test_different_beneficiaries_allowed_for_same_incident(self):
        set_distribution_repetitions(1)
        inc, item, wh = self._make_item_env(7)
        ben_a = self.create_beneficiary()
        ben_b = self.create_beneficiary()
        payload_a = self._items_payload(inc, item, wh)
        payload_a['beneficiaries'] = [
            {'family_name': ben_a['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben_a['id']},
        ]
        payload_b = self._items_payload(inc, item, wh)
        payload_b['beneficiaries'] = [
            {'family_name': ben_b['name'], 'members': 3, 'item': None, 'quantity': 2,
             'beneficiary_id': ben_b['id']},
        ]
        r1 = self.client.post('/api/distributions', json=payload_a)
        self.assertEqual(r1.status_code, 201, r1.get_json())
        r2 = self.client.post('/api/distributions', json=payload_b)
        self.assertEqual(r2.status_code, 201, r2.get_json())

    def test_repetitions_settings_roundtrip_and_api(self):
        resp = self.client.post('/api/settings/distribution_repetitions', json={'value': 3})
        self.assertEqual(resp.status_code, 200, resp.get_json())
        resp = self.client.get('/api/settings/distribution_repetitions')
        self.assertEqual(resp.get_json()['value'], 3)
        with app_module.app.app_context():
            self.assertEqual(app_module.get_distribution_repetitions('2081/82'), 3)
        resp = self.client.get('/api/data')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['distribution_repetitions'], 3)
        self.assertEqual(data['active_distribution_repetitions'], 3)
