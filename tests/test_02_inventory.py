import uuid
from tests.conftest import LeocTestCase, app_module


class InventoryManagementTest(LeocTestCase):
    def test_category_crud(self):
        self.login()
        name = f'TestCat-{uuid.uuid4().hex[:6]}'
        resp = self.client.post('/api/categories', json={'name': name, 'description': 'Test'})
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['name'], name)

        cat_id = data['id']
        resp = self.client.get('/api/categories')
        self.assertEqual(resp.status_code, 200)
        names = [c['name'] for c in resp.get_json()['categories']]
        self.assertIn(name, names)

        resp = self.client.put(f'/api/categories/{cat_id}', json={'description': 'Updated'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.delete(f'/api/categories/{cat_id}')
        self.assertEqual(resp.status_code, 200)

    def test_predefined_category_not_deletable(self):
        self.login()
        resp = self.client.get('/api/categories')
        predef = [c for c in resp.get_json()['categories'] if c['is_predefined']]
        if predef:
            resp = self.client.delete(f'/api/categories/{predef[0]["id"]}')
            self.assertEqual(resp.status_code, 400)

    def test_warehouse_crud(self):
        self.login()
        name = f'WH-{uuid.uuid4().hex[:6]}'
        resp = self.client.post('/api/warehouses', json={
            'name': name, 'code': 'WH-001', 'address': 'Main St',
            'contact_person': 'John', 'phone': '9800000001', 'capacity': 5000,
            'remarks': 'Main warehouse',
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['name'], name)

        wh_id = data['id']
        resp = self.client.get(f'/api/warehouses/{wh_id}')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.put(f'/api/warehouses/{wh_id}', json={'capacity': 10000})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['data']['capacity'], 10000)

    def test_warehouse_zone_crud(self):
        self.login()
        wh = self.create_warehouse()
        resp = self.client.post('/api/warehouse-zones', json={
            'warehouse_id': wh['id'], 'name': 'Zone A', 'code': 'ZA', 'capacity': 500,
        })
        self.assertEqual(resp.status_code, 201)
        zone = resp.get_json()['data']
        self.assertEqual(zone['name'], 'Zone A')

        zone_id = zone['id']
        resp = self.client.put(f'/api/warehouse-zones/{zone_id}', json={'name': 'Zone Alpha'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/warehouse-zones?warehouse_id={wh["id"]}')
        self.assertEqual(resp.status_code, 200)

    def test_supplier_crud(self):
        self.login()
        phone = f'98{uuid.uuid4().int % 100000000:08d}'
        email = f'sup{uuid.uuid4().hex[:4]}@test.com'
        resp = self.client.post('/api/suppliers', json={
            'name': 'Test Supplier', 'phone': phone, 'email': email,
            'address': 'Kathmandu', 'supplier_type': 'Local',
        })
        self.assertEqual(resp.status_code, 201)
        sup = resp.get_json()['data']

        sup_id = sup['id']
        resp = self.client.put(f'/api/suppliers/{sup_id}', json={'status': 'Inactive'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/suppliers/{sup_id}')
        self.assertEqual(resp.status_code, 200)

    def test_item_crud(self):
        self.login()
        cat = self.create_category()
        name = f'Rice-{uuid.uuid4().hex[:6]}'
        resp = self.client.post('/api/items', json={
            'name': name, 'unit': 'Kg', 'category_id': cat['id'],
            'minimum_stock': 10, 'max_stock': 100,
            'expiry_tracking': True, 'batch_tracking': True,
            'is_consumable': True, 'storage_requirement': 'Dry',
        })
        self.assertEqual(resp.status_code, 201)
        item = resp.get_json()['data']
        self.assertEqual(item['name'], name)
        self.assertIsNotNone(item['item_code'])

        item_id = item['id']
        resp = self.client.put(f'/api/items/{item_id}', json={'local_name': 'चामल'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'/api/items/{item_id}')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/items')
        self.assertEqual(resp.status_code, 200)
        names = [i['name'] for i in resp.get_json()['items']]
        self.assertIn(name, names)

    def test_item_filter_by_category(self):
        self.login()
        cat1 = self.create_category(name=f'Food-{uuid.uuid4().hex[:6]}')
        cat2 = self.create_category(name=f'Medical-{uuid.uuid4().hex[:6]}')
        item1 = self.create_item(cat1['id'], name=f'Rice-{uuid.uuid4().hex[:6]}')
        item2 = self.create_item(cat2['id'], name=f'Bandage-{uuid.uuid4().hex[:6]}')

        resp = self.client.get(f'/api/items?category_id={cat1["id"]}')
        names = [i['name'] for i in resp.get_json()['items']]
        self.assertIn(item1['name'], names)
        self.assertNotIn(item2['name'], names)

    def test_stock_receipt_with_full_details(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        sup = self.create_supplier()

        resp = self.client.post('/api/stock-receipts', json={
            'warehouse_id': wh['id'],
            'supplier_id': sup['id'],
            'source_type': 'Purchase',
            'source_name': 'Local Market',
            'date': '2082-03-15',
            'ref_number': 'REF-001',
            'invoice_no': 'INV-001',
            'invoice_date': '2082-03-10',
            'delivery_note': 'DN-001',
            'vehicle_no': 'BA 1 JA 1234',
            'received_by': 'Ram Shrestha',
            'verified_by': 'Hari Gurung',
            'remarks': 'First batch',
            'items': [{
                'item_id': item['id'], 'quantity': 50, 'unit': 'Piece',
                'batch_no': 'B001', 'serial_no': 'S001',
                'mfg_date': '2081-06-01', 'expiry_date': '2084-06-01',
                'unit_cost': 15.0,
            }],
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['source_type'], 'Purchase')
        self.assertEqual(data['vehicle_no'], 'BA 1 JA 1234')
        self.assertIsNotNone(data['receipt_no'])

        receipt_id = data['id']
        resp = self.client.get(f'/api/stock-receipts/{receipt_id}')
        self.assertEqual(resp.status_code, 200)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 50)

    def test_stock_receipt_update_updates_inventory(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        receipt = self.create_stock_receipt(wh['id'], item['id'], quantity=10)

        receipt_id = receipt['id']
        resp = self.client.put(f'/api/stock-receipts/{receipt_id}', json={
            'warehouse_id': wh['id'],
            'source_type': 'Donation',
            'date': '2082-03-01',
            'items': [{
                'item_id': item['id'], 'quantity': 20, 'unit': 'Piece',
                'unit_cost': 12.5,
                'mfg_date': '2081-09-01', 'expiry_date': '2083-09-01',
            }],
        })
        self.assertEqual(resp.status_code, 200)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 20)

    def test_inventory_summary_and_filters(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item1 = self.create_item(cat['id'], name=f'ItemA-{uuid.uuid4().hex[:6]}', min_stock=5)
        item2 = self.create_item(cat['id'], name=f'ItemB-{uuid.uuid4().hex[:6]}', min_stock=3)
        self.create_stock_receipt(wh['id'], item1['id'], quantity=10)
        self.create_stock_receipt(wh['id'], item2['id'], quantity=2)

        resp = self.client.get(f'/api/inventory?warehouse_id={wh["id"]}')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.get_json()['inventory']) >= 2)

        resp = self.client.get('/api/inventory/summary')
        self.assertEqual(resp.status_code, 200)
        summary = resp.get_json()
        self.assertIn('total_items', summary)
        self.assertIn('total_quantity', summary)

    def test_manual_adjustment_increase_decrease(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)

        # Increase by 5
        resp = self.client.post('/api/adjustments', json={
            'item_id': item['id'], 'warehouse_id': wh['id'],
            'adjustment_type': 'Increase', 'adjusted_quantity': 5,
            'reason': 'Found in storage', 'date': '2082-04-01',
        })
        self.assertEqual(resp.status_code, 201)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 25)

        # Decrease by 3
        resp = self.client.post('/api/adjustments', json={
            'item_id': item['id'], 'warehouse_id': wh['id'],
            'adjustment_type': 'Decrease', 'adjusted_quantity': 3,
            'reason': 'Damage', 'date': '2082-04-02',
        })
        self.assertEqual(resp.status_code, 201)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 22)

    def test_stock_transfer_between_warehouses(self):
        self.login()
        cat = self.create_category()
        wh1 = self.create_warehouse(name=f'Source-{uuid.uuid4().hex[:6]}')
        wh2 = self.create_warehouse(name=f'Dest-{uuid.uuid4().hex[:6]}')
        item = self.create_item(cat['id'])
        self.create_stock_receipt(wh1['id'], item['id'], quantity=15)

        resp = self.client.post('/api/stock-transfers', json={
            'from_warehouse_id': wh1['id'], 'to_warehouse_id': wh2['id'],
            'transfer_date': '2082-04-01', 'reason': 'Replenishment',
            'items': [{'item_id': item['id'], 'quantity': 5, 'unit': 'Piece'}],
        })
        self.assertEqual(resp.status_code, 201)
        transfer = resp.get_json()['data']
        self.assertIsNotNone(transfer['transfer_no'])

        with app_module.app.app_context():
            inv1 = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh1['id']).first()
            inv2 = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh2['id']).first()
            self.assertEqual(inv1.quantity, 10)
            self.assertEqual(inv2.quantity, 5)

    def test_inventory_status_calculations(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'], min_stock=10, max_stock=100)

        with app_module.app.app_context():
            inv = app_module.Inventory(item_id=item['id'], warehouse_id=wh['id'], quantity=5)
            app_module.db.session.add(inv)
            app_module.db.session.commit()
            self.assertEqual(inv.status, 'low_stock')

            inv.quantity = 0
            app_module.db.session.commit()
            self.assertEqual(inv.status, 'out_of_stock')

            inv.quantity = 50
            app_module.db.session.commit()
            self.assertEqual(inv.status, 'available')

    def test_item_history(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        self.create_stock_receipt(wh['item_id'], item['id'], quantity=10)

        resp = self.client.get(f"/api/items/{item['id']}/history")
        self.assertEqual(resp.status_code, 200)
        history = resp.get_json()
        self.assertIn('receipts', history)
        self.assertIn('adjustments', history)
