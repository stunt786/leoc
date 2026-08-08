import uuid
from tests.conftest import LeocTestCase, app_module


class ValidationEdgeCaseTest(LeocTestCase):
    def test_validate_phone(self):
        self.assertTrue(app_module.validate_phone('9800000000'))
        self.assertTrue(app_module.validate_phone('+977 98-0000-0000'))
        self.assertTrue(app_module.validate_phone('01-4123456'))
        self.assertFalse(app_module.validate_phone('abc'))
        self.assertFalse(app_module.validate_phone('12'))
        self.assertTrue(app_module.validate_phone(''))

    def test_is_valid_nepali_date(self):
        self.assertTrue(app_module.is_valid_nepali_date('2082-01-01'))
        self.assertTrue(app_module.is_valid_nepali_date('2090-12-30'))
        self.assertFalse(app_module.is_valid_nepali_date('2082-13-01'))
        self.assertFalse(app_module.is_valid_nepali_date('9999-01-01'))
        self.assertFalse(app_module.is_valid_nepali_date('2082/01/01'))
        self.assertFalse(app_module.is_valid_nepali_date(''))
        self.assertFalse(app_module.is_valid_nepali_date(None))

    def test_parse_int_field(self):
        self.assertEqual(app_module.parse_int_field({'x': '7'}, 'x', minimum=1), 7)
        self.assertEqual(app_module.parse_int_field({'x': None}, 'x', default=0), 0)
        with self.assertRaises(ValueError):
            app_module.parse_int_field({'x': 'abc'}, 'x')

    def test_parse_float_field(self):
        self.assertEqual(app_module.parse_float_field({'x': '12.5'}, 'x', minimum=0), 12.5)
        self.assertEqual(app_module.parse_float_field({'x': ''}, 'x', default=0.0), 0.0)
        with self.assertRaises(ValueError):
            app_module.parse_float_field({'x': 'abc'}, 'x')

    def test_parse_bool_field(self):
        self.assertTrue(app_module.parse_bool_field({'x': 'true'}, 'x'))
        self.assertTrue(app_module.parse_bool_field({'x': 'yes'}, 'x'))
        self.assertTrue(app_module.parse_bool_field({'x': '1'}, 'x'))
        self.assertFalse(app_module.parse_bool_field({'x': 'false'}, 'x'))
        self.assertFalse(app_module.parse_bool_field({'x': 'no'}, 'x'))
        self.assertFalse(app_module.parse_bool_field({'x': '0'}, 'x'))
        self.assertFalse(app_module.parse_bool_field({'x': None}, 'x'))

    def test_parse_date_field(self):
        d = app_module.parse_date_field({'d': '2026-06-23'}, 'd')
        self.assertEqual(d.isoformat(), '2026-06-23')
        self.assertIsNone(app_module.parse_date_field({'d': None}, 'd'))
        with self.assertRaises(ValueError):
            app_module.parse_date_field({'d': '2026/06/23'}, 'd')

    def test_parse_bs_date_field(self):
        d = app_module.parse_bs_date_field({'d': '2082-01-01'}, 'd')
        self.assertEqual(d.isoformat(), '2025-04-14')
        with self.assertRaises(ValueError):
            app_module.parse_bs_date_field({'d': '2082-13-01'}, 'd')

    def test_bs_date_conversion(self):
        self.assertEqual(app_module.ad_to_bs(2025, 4, 14), '2082-01-01')
        self.assertEqual(app_module.ad_to_bs(2026, 4, 14), '2083-01-01')
        self.assertEqual(app_module.bs_to_ad('2082-01-01'), '2025-04-14')
        self.assertEqual(app_module.bs_to_ad('2083-01-01'), '2026-04-14')
        self.assertIsNone(app_module.bs_to_ad('invalid'))
        self.assertIsNone(app_module.bs_to_ad(None))

    def test_invalid_ward_rejected(self):
        self.login()
        resp = self.client.post('/api/incidents', json={
            'incident_name': 'Test', 'incident_type': 'Flood', 'ward': 99,
            'coordinates': '28.5,81.5',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Invalid ward', resp.get_json()['message'])

    def test_empty_category_name_rejected(self):
        self.login()
        resp = self.client.post('/api/categories', json={'name': '', 'description': 'x'})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('required', resp.get_json()['message'])

    def test_future_distribution_date_rejected(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=10)

        resp = self.client.post('/api/distributions', json={
            'warehouse_id': wh['id'], 'incident_id': inc['id'],
            'destination': 'Test', 'receiver': 'Test',
            'distribution_date': '2099-01-01',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 4, 'unit': 'Piece'}],
            'beneficiaries': [{'family_name': 'A', 'quantity': 4}],
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('future', resp.get_json()['message'])

    def test_same_warehouse_transfer_rejected(self):
        self.login()
        wh = self.create_warehouse()
        resp = self.client.post('/api/stock-transfers', json={
            'from_warehouse_id': wh['id'], 'to_warehouse_id': wh['id'],
            'transfer_date': '2082-03-01',
            'items': [{'item_id': 1, 'quantity': 1, 'unit': 'Piece'}],
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('different', resp.get_json()['message'])

    def test_invalid_adjustment_type_rejected(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        resp = self.client.post('/api/adjustments', json={
            'item_id': item['id'], 'warehouse_id': wh['id'],
            'adjustment_type': 'InvalidType', 'adjusted_quantity': 1,
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Invalid adjustment', resp.get_json()['message'])

    def test_cash_receipt_missing_amount_rejected(self):
        self.login()
        fund = self.create_fund()
        resp = self.client.post('/api/cash-receipts', json={
            'fund_id': fund['id'], 'receipt_date': '2082-03-01',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('required', resp.get_json()['message'])

    def test_duplicate_beneficiary_phone_rejected(self):
        self.login()
        ben = self.create_beneficiary()
        resp = self.client.post('/api/beneficiaries', json={
            'name': 'Other', 'national_id': 'DIFF-ID',
            'phone': ben['phone'], 'ward': 1, 'tole': 'Tole',
        })
        self.assertEqual(resp.status_code, 400)

    def test_duplicate_beneficiary_national_id_rejected(self):
        self.login()
        ben = self.create_beneficiary()
        resp = self.client.post('/api/beneficiaries', json={
            'name': 'Other', 'national_id': ben['national_id'],
            'phone': '9800000001', 'ward': 1, 'tole': 'Tole',
        })
        self.assertEqual(resp.status_code, 400)

    def test_distribution_cancel_without_reason(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=10)
        dist = self.create_distribution(wh['id'], inc['id'], item['id'], quantity=4)

        resp = self.client.post(f"/api/distributions/{dist['id']}/cancel", json={})
        self.assertEqual(resp.status_code, 400)

    def test_distribution_exceeds_available_stock_rejected(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=2)

        resp = self.client.post('/api/distributions', json={
            'warehouse_id': wh['id'], 'incident_id': inc['id'],
            'destination': 'Ward 1', 'receiver': 'Test',
            'distribution_date': '2082-03-03', 'officer': 'Test',
            'items': [{'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 5, 'unit': 'Piece'}],
            'beneficiaries': [
                {'family_name': 'A', 'members': 2, 'item': None, 'quantity': 5},
            ],
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Insufficient stock', resp.get_json()['message'])

    def test_not_found_returns_404(self):
        self.login()
        resp = self.client.put('/api/items/999999', json={'name': 'x'})
        self.assertEqual(resp.status_code, 404)

    def test_missing_category_returns_404(self):
        self.login()
        resp = self.client.post('/api/items', json={
            'name': 'NoCat', 'unit': 'Piece', 'category_id': 999999,
        })
        self.assertEqual(resp.status_code, 404)


class ReportGenerationTest(LeocTestCase):
    def create_setup_data(self):
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)
        dist = self.create_distribution(wh['id'], inc['id'], item['id'], quantity=5)
        return cat, wh, item, inc, dist

    def test_print_report_html(self):
        self.login()
        self.create_setup_data()
        resp = self.client.get('/print-report/inventory')
        self.assertEqual(resp.status_code, 200)

    def test_report_data_json(self):
        self.login()
        self.create_setup_data()
        resp = self.client.get('/api/reports-data/inventory')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get('success', False))

    def test_pdf_report_dispatch(self):
        self.login()
        cat, wh, item, inc, dist = self.create_setup_data()
        resp = self.client.get('/api/reports/dispatch')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/pdf', resp.headers.get('Content-Type', ''))

    def test_pdf_report_distribution(self):
        self.login()
        cat, wh, item, inc, dist = self.create_setup_data()
        resp = self.client.get('/api/reports/distribution')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/pdf', resp.headers.get('Content-Type', ''))

    def test_pdf_report_incidents(self):
        self.login()
        inc = self.create_incident()
        resp = self.client.get('/api/reports/incidents')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/pdf', resp.headers.get('Content-Type', ''))

    def test_pdf_report_adjustments(self):
        self.login()
        self.create_setup_data()
        resp = self.client.get('/api/reports/adjustments')
        self.assertEqual(resp.status_code, 200)

    def test_pdf_report_low_stock(self):
        self.login()
        resp = self.client.get('/api/reports/low-stock')
        self.assertEqual(resp.status_code, 200)

    def test_pdf_report_monthly_summary(self):
        self.login()
        self.create_setup_data()
        resp = self.client.get('/api/reports/monthly-summary')
        self.assertEqual(resp.status_code, 200)

    def test_pdf_report_inventory(self):
        self.login()
        self.create_setup_data()
        resp = self.client.get('/api/reports/inventory')
        self.assertEqual(resp.status_code, 200)

    def test_pdf_report_stock_receipts(self):
        self.login()
        self.create_setup_data()
        resp = self.client.get('/api/reports/stock-receipts')
        self.assertEqual(resp.status_code, 200)

    def test_pdf_report_cash_balance(self):
        self.login()
        inc = self.create_incident(name=f'Rep-{uuid.uuid4().hex[:6]}', ward=2)
        fund = self.create_fund()
        self.create_cash_receipt(fund['id'], amount=10000)
        cash_req = self.create_cash_request(inc['id'], amount=5000)
        self.create_cash_distribution(fund['id'], inc['id'], cash_req['id'], amount=3000)

        resp = self.client.get('/api/reports/cash-balance')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/reports/cash-receipts')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/reports/cash-requests')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/reports/cash-distributions')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/reports/cash-by-incident')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/reports/cash-by-funding-source')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/reports/cash-yearly')
        self.assertEqual(resp.status_code, 200)

    def test_print_individual_documents(self):
        self.login()
        cat, wh, item, inc, dist = self.create_setup_data()

        resp = self.client.get(f'/api/distributions/{dist["id"]}/print')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/incidents/{inc["id"]}/print')
        self.assertEqual(resp.status_code, 200)

    def test_bin_card_and_stock_book(self):
        self.login()
        cat, wh, item, inc, dist = self.create_setup_data()

        resp = self.client.get(f'/api/inventory/bin-card?item_id={item["id"]}&warehouse_id={wh["id"]}')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/inventory/stock-book?warehouse_id={wh["id"]}')
        self.assertEqual(resp.status_code, 200)

    def test_daily_report_preview(self):
        self.login()
        inc = self.create_incident()
        resp = self.client.get('/daily-report-preview')
        self.assertEqual(resp.status_code, 200)
