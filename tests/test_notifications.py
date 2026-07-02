from datetime import datetime, timedelta, timezone
import uuid

from tests.conftest import LeocTestCase, app_module


class NotificationSystemTest(LeocTestCase):
    def setUp(self):
        super().setUp()
        with app_module.app.app_context():
            app_module.db.session.execute(app_module.db.text('DELETE FROM notification'))
            app_module.db.session.commit()
        app_module.LAST_STATUS_CHECK_TIME = 0

    def _create_inventory_receipt(self, low_stock=False):
        self.login()
        category = self.create_category(name=f'NotifCat-{uuid.uuid4().hex[:8]}')
        warehouse = self.create_warehouse(name=f'NotifWh-{uuid.uuid4().hex[:8]}')
        item = self.create_item(
            category['id'],
            name=f'NotifItem-{uuid.uuid4().hex[:8]}',
            min_stock=20 if low_stock else 2,
            max_stock=100,
        )
        quantity = 5 if low_stock else 50
        self.create_stock_receipt(warehouse['id'], item['id'], quantity=quantity)
        return warehouse, item

    def test_notifications_page_loads_and_clear_all_works(self):
        self._create_inventory_receipt(low_stock=False)

        app_module.LAST_STATUS_CHECK_TIME = 0
        resp = self.client.get('/api/notifications')
        self.assertEqual(resp.status_code, 200, resp.get_json())
        data = resp.get_json()
        self.assertTrue(any(n['type'] == 'stock_receipt' for n in data['notifications']))

        page = self.client.get('/notifications')
        self.assertEqual(page.status_code, 200)

        clear_resp = self.client.post('/api/notifications/clear')
        self.assertEqual(clear_resp.status_code, 200, clear_resp.get_json())

        app_module.LAST_STATUS_CHECK_TIME = 0
        after = self.client.get('/api/notifications')
        self.assertEqual(after.status_code, 200, after.get_json())
        self.assertEqual(after.get_json()['notifications'], [])

    def test_low_stock_resurfaces_after_24_hours(self):
        self._create_inventory_receipt(low_stock=True)

        app_module.LAST_STATUS_CHECK_TIME = 0
        first = self.client.get('/api/notifications')
        self.assertEqual(first.status_code, 200, first.get_json())
        notifications = first.get_json()['notifications']
        low_stock = next((n for n in notifications if n['type'] == 'low_stock'), None)
        self.assertIsNotNone(low_stock)

        clear_resp = self.client.post(f"/api/notifications/{low_stock['id']}/clear")
        self.assertEqual(clear_resp.status_code, 200, clear_resp.get_json())

        with app_module.app.app_context():
            notif = app_module.Notification.query.get(low_stock['id'])
            notif.cleared = True
            notif.cleared_at = datetime.now(timezone.utc) - timedelta(hours=25)
            app_module.db.session.commit()

        app_module.LAST_STATUS_CHECK_TIME = 0
        resurfaced = self.client.get('/api/notifications')
        self.assertEqual(resurfaced.status_code, 200, resurfaced.get_json())
        refreshed = resurfaced.get_json()['notifications']
        self.assertTrue(any(n['type'] == 'low_stock' and not n['cleared'] for n in refreshed))
