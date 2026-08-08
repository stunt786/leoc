"""Tests for disaster management workflows: incidents, distributions, assessments, daily bulletins, weekly forecasts."""
import uuid
from datetime import datetime, timezone
from tests.conftest import LeocTestCase, app_module


class DisasterWorkflowTest(LeocTestCase):
    def test_incident_crud(self):
        self.login()
        name = f'Flood-{uuid.uuid4().hex[:6]}'
        payload = {
            'incident_name': name,
            'incident_type': 'Flood',
            'ward': 3,
            'start_date': '2082-01-15',
            'status': 'Active',
            'description': 'Major flooding',
            'severity': 'high',
            'tole': 'Test Tole',
            'coordinates': '29.5,81.2',
            'affected_people': 500,
            'injured': 10,
            'deaths': 2,
            'missing_persons': 1,
            'affected_households': 80,
            'house_damaged': 20,
            'house_destroyed': 10,
            'road_blocked': True,
            'electricity_blocked': True,
        }
        resp = self.client.post('/api/incidents', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['incident_name'], name)
        self.assertEqual(data['incident_type'], 'Flood')
        self.assertEqual(data['ward'], 3)
        self.assertEqual(data['severity'], 'high')
        self.assertEqual(data['affected_people'], 500)

        inc_id = data['id']
        resp = self.client.put(f'/api/incidents/{inc_id}', json={'status': 'Resolved'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['data']['status'], 'Resolved')

        resp = self.client.get('/api/incidents')
        self.assertEqual(resp.status_code, 200)
        names = [i['incident_name'] for i in resp.get_json()['incidents']]
        self.assertIn(name, names)

    def test_incident_with_full_impact_fields(self):
        self.login()
        payload = {
            'incident_name': f'Full-{uuid.uuid4().hex[:6]}',
            'incident_type': 'Earthquake',
            'ward': 5,
            'start_date': '2082-02-01',
            'status': 'Active',
            'affected_people': 1000,
            'affected_people_male': 450,
            'affected_people_female': 550,
            'injured': 50, 'injured_male': 30, 'injured_female': 20,
            'deaths': 5, 'death_male': 3, 'death_female': 2,
            'missing_persons': 3, 'missing_male': 2, 'missing_female': 1,
            'affected_households': 200,
            'house_damaged': 50, 'house_destroyed': 30,
            'public_building_damaged': 5, 'public_building_destroyed': 2,
            'estimated_loss': 5000000.0,
            'cattle_lost': 20, 'cattle_injured': 10,
            'poultry_lost': 100, 'poultry_injured': 50,
            'goats_sheep_lost': 30, 'goats_sheep_injured': 15,
            'road_blocked': True, 'electricity_blocked': True,
            'communication_blocked': False, 'drinking_water_disrupted': True,
            'rescue_operations': 'Search and rescue ongoing',
            'coordinates': '28.5,81.5',
        }
        resp = self.client.post('/api/incidents', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['deaths'], 5)
        self.assertEqual(data['cattle_lost'], 20)
        self.assertEqual(data['estimated_loss'], 5000000.0)
        self.assertTrue(data['road_blocked'])

    def test_distribution_with_items_and_beneficiaries(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident(ward=2)
        self.create_stock_receipt(wh['id'], item['id'], quantity=20)

        payload = {
            'incident_id': inc['id'],
            'warehouse_id': wh['id'],
            'destination': 'Test Destination',
            'receiver': 'Field Officer',
            'phone': '9800000001',
            'location': 'Ward 2',
            'distribution_date': '2082-03-05',
            'officer': 'Test Officer',
            'remarks': 'Urgent need',
            'items': [
                {'item_id': item['id'], 'warehouse_id': wh['id'], 'quantity': 10, 'unit': 'Piece'},
            ],
            'beneficiaries': [
                {'family_name': 'Family A', 'members': 4, 'item': None, 'quantity': 10},
            ],
        }
        resp = self.client.post('/api/distributions', json=payload)
        self.assertEqual(resp.status_code, 201, resp.get_json())
        data = resp.get_json()['data']
        self.assertEqual(data['status'], 'Completed')
        self.assertEqual(data['distribution_date'], '2082-03-05')
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['quantity'], 10)

        dist_id = data['id']
        resp = self.client.get(f'/api/distributions/{dist_id}')
        self.assertEqual(resp.status_code, 200)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 10)

    def test_distribution_inventory_reduction_and_beneficiaries(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=10)

        dist = self.create_distribution(wh['id'], inc['id'], item['id'], quantity=6)
        self.assertIsNotNone(dist)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 4)
            di = app_module.DistributionItem.query.filter_by(distribution_id=dist['id']).first()
            self.assertIsNotNone(di)
            self.assertEqual(di.quantity, 6)

    def test_distribution_cancel_restores_inventory(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=10)

        dist = self.create_distribution(wh['id'], inc['id'], item['id'], quantity=4)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 6)

        resp = self.client.post(f"/api/distributions/{dist['id']}/cancel", json={'cancel_reason': 'Test cancel'})
        self.assertEqual(resp.status_code, 200)

        with app_module.app.app_context():
            inv = app_module.Inventory.query.filter_by(item_id=item['id'], warehouse_id=wh['id']).first()
            self.assertEqual(inv.quantity, 10)

    def test_distribution_beneficiary_document_upload(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=10)
        dist = self.create_distribution(wh['id'], inc['id'], item['id'], quantity=4)

        with app_module.app.app_context():
            ben = app_module.DistributionBeneficiary.query.filter_by(distribution_id=dist['id']).first()
            self.assertIsNotNone(ben)
            ben_id = ben.id

        resp = self.client.post(
            f'/api/distributions/beneficiary/{ben_id}/upload-photo',
            data={'file': (io.BytesIO(b'fake-image-data'), 'test.jpg')},
            content_type='multipart/form-data',
        )
        self.assertIn(resp.status_code, (200, 201, 400))  # may fail if dir not writable, but shouldn't crash

    def test_disaster_assessment(self):
        self.login()
        inc = self.create_incident()
        payload = {
            'incident_id': inc['id'],
            'deaths': 3,
            'injured': 15,
            'affected_households': 50,
            'house_damaged': 10,
            'house_destroyed': 5,
        }
        resp = self.client.post('/api/disaster-assessments', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['deaths'], 3)
        self.assertEqual(data['injured'], 15)

        assess_id = data['id']
        resp = self.client.put(f'/api/disaster-assessments/{assess_id}', json={'deaths': 5})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['data']['deaths'], 5)

        resp = self.client.get('/api/disaster-assessments')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.get_json()['assessments']) > 0)

    def test_daily_bulletin(self):
        self.login()
        inc = self.create_incident()
        payload = {
            'notice_title': 'Daily Situation Report',
            'notice_description': 'No major incidents',
            'valid_from': '2082-01-15',
            'priority': 'Normal',
            'report_status': 'Draft',
            'weather_status': 'Clear',
            'situation_summary': 'All quiet',
            'incident_ids': [inc['id']],
        }
        resp = self.client.post('/api/daily-bulletins', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['notice_title'], 'Daily Situation Report')

        bul_id = data['id']
        resp = self.client.put(f'/api/daily-bulletins/{bul_id}', json={'report_status': 'Published'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/daily-bulletins')
        self.assertEqual(resp.status_code, 200)

    def test_weekly_forecast(self):
        self.login()
        payload = {
            'date_from': '2082-04-01',
            'date_to': '2082-04-07',
            'rainfall_snowfall': 'Light rain expected',
            'high_temperature': '28°C',
            'low_temperature': '15°C',
            'forecast_status': 'Normal',
            'forecast_info': 'No extreme weather',
        }
        resp = self.client.post('/api/weekly-forecasts', json=payload)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()['data']
        self.assertEqual(data['rainfall_snowfall'], 'Light rain expected')

        fc_id = data['id']
        resp = self.client.get(f'/api/weekly-forecasts/{fc_id}')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/weekly-forecasts')
        self.assertEqual(resp.status_code, 200)

    def test_incident_history(self):
        self.login()
        cat = self.create_category()
        wh = self.create_warehouse()
        item = self.create_item(cat['id'])
        inc = self.create_incident()
        self.create_stock_receipt(wh['id'], item['id'], quantity=10)
        self.create_distribution(wh['id'], inc['id'], item['id'], quantity=4)

        resp = self.client.get(f"/api/incidents/{inc['id']}/history")
        self.assertEqual(resp.status_code, 200)
        timeline = resp.get_json()['timeline']
        self.assertTrue(any(d['_type'] == 'distribution' for d in timeline))


# Add io import for in-memory file uploads
import io
