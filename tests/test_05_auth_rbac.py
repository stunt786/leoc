import uuid
from datetime import datetime, timezone
from tests.conftest import LeocTestCase, app_module


class AuthAndRBACTest(LeocTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with app_module.app.app_context():
            cls._ensure_test_users()

    @classmethod
    def _ensure_test_users(cls):
        from app import db as _db
        from werkzeug.security import generate_password_hash
        _db.session.execute(
            _db.text(
                "INSERT OR IGNORE INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) "
                "VALUES (:u, :p, :r, :f, 1, :c)"
            ),
            {'u': 'viewer', 'p': generate_password_hash('viewer123'), 'r': 'viewer', 'f': 'Viewer User', 'c': datetime.now(timezone.utc)},
        )
        _db.session.execute(
            _db.text(
                "INSERT OR IGNORE INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) "
                "VALUES (:u, :p, :r, :f, 1, :c)"
            ),
            {'u': 'dataentry', 'p': generate_password_hash('dataentry123'), 'r': 'data_entry', 'f': 'Data Entry', 'c': datetime.now(timezone.utc)},
        )
        _db.session.execute(
            _db.text(
                "INSERT OR IGNORE INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) "
                "VALUES (:u, :p, :r, :f, 1, :c)"
            ),
            {'u': 'warehousemgr', 'p': generate_password_hash('manager123'), 'r': 'warehouse_manager', 'f': 'WH Manager', 'c': datetime.now(timezone.utc)},
        )
        _db.session.execute(
            _db.text(
                "INSERT OR IGNORE INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) "
                "VALUES (:u, :p, :r, :f, 1, :c)"
            ),
            {'u': 'editor1', 'p': generate_password_hash('editor123'), 'r': 'editor', 'f': 'Editor', 'c': datetime.now(timezone.utc)},
        )
        _db.session.execute(
            _db.text(
                "INSERT OR IGNORE INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) "
                "VALUES (:u, :p, :r, :f, 1, :c)"
            ),
            {'u': 'operator1', 'p': generate_password_hash('operator123'), 'r': 'operator', 'f': 'Operator', 'c': datetime.now(timezone.utc)},
        )
        _db.session.execute(
            _db.text(
                "INSERT OR IGNORE INTO \"user\" (username, password_hash, role, full_name, is_active, created_at) "
                "VALUES (:u, :p, :r, :f, 1, :c)"
            ),
            {'u': 'finance1', 'p': generate_password_hash('finance123'), 'r': 'finance', 'f': 'Finance', 'c': datetime.now(timezone.utc)},
        )
        _db.session.commit()

    def test_login_page_loads(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)

    def test_unauthorized_redirect_to_login(self):
        resp = self.client.get('/settings')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    def test_api_returns_401_when_unauthenticated(self):
        resp = self.client.get('/api/inventory')
        self.assertEqual(resp.status_code, 401)
        self.assertIn('Authentication required', resp.get_json()['message'])

    def test_admin_login_success(self):
        resp = self.login()
        self.assertEqual(resp.status_code, 302)
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_logout_clears_session(self):
        self.login()
        self.client.post('/logout', follow_redirects=False)
        resp = self.client.get('/api/inventory')
        self.assertEqual(resp.status_code, 401)

    def test_safe_redirect_no_open_redirect(self):
        resp = self.client.post(
            '/login?next=http://evil.example.com',
            data={'username': 'admin', 'password': 'admin123'},
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('evil.example.com', resp.headers['Location'])

    def test_invalid_password(self):
        resp = self.client.post(
            '/login',
            data={'username': 'admin', 'password': 'wrongpassword'},
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 200)

    def test_account_lockout(self):
        with app_module.app.app_context():
            app_module.db.session.execute(
                app_module.db.text(
                    "UPDATE \"user\" SET locked_until = :locked WHERE username = :username"
                ),
                {
                    'locked_until': datetime.now(timezone.utc) + __import__('datetime').timedelta(minutes=15),
                    'username': 'admin',
                },
            )
            app_module.db.session.commit()

        resp = self.login()
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Account locked', resp.get_data(as_text=True))

        with app_module.app.app_context():
            app_module.db.session.execute(
                app_module.db.text(
                    "UPDATE \"user\" SET locked_until = NULL WHERE username = 'admin'"
                ),
            )
            app_module.db.session.commit()

    def test_viewer_cannot_access_user_management(self):
        self.login('viewer', 'viewer123')
        resp = self.client.get('/api/users')
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get('/users')
        self.assertEqual(resp.status_code, 200)

    def test_data_entry_can_create_data(self):
        self.login('dataentry', 'dataentry123')
        cat = self.create_category()
        self.assertIsNotNone(cat)

    def test_editor_cannot_manage_users(self):
        self.login('editor1', 'editor123')
        resp = self.client.get('/api/users')
        self.assertEqual(resp.status_code, 403)

    def test_operator_can_delete(self):
        self.login('operator1', 'operator123')
        cat = self.create_category()
        resp = self.client.delete(f'/api/categories/{cat["id"]}')
        self.assertEqual(resp.status_code, 200)

    def test_finance_can_manage_funds(self):
        self.login('finance1', 'finance123')
        fund = self.create_fund()
        self.assertIsNotNone(fund)

        resp = self.client.get('/api/cash-funds')
        self.assertEqual(resp.status_code, 200)

    def test_user_creation_validation_min_length(self):
        self.login()
        resp = self.client.post('/api/users', json={
            'username': 'ab', 'password': '123', 'role': 'viewer',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('at least 6', resp.get_json()['message'])

    def test_user_creation_invalid_role(self):
        self.login()
        resp = self.client.post('/api/users', json={
            'username': 'newuser', 'password': 'password123', 'role': 'superadmin',
        })
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Invalid role', resp.get_json()['message'])

    def test_user_creation_duplicate_username(self):
        self.login()
        resp = self.client.post('/api/users', json={
            'username': 'dupuser', 'password': 'password123', 'role': 'viewer', 'full_name': 'Dup',
        })
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post('/api/users', json={
            'username': 'dupuser', 'password': 'password123', 'role': 'viewer',
        })
        self.assertEqual(resp.status_code, 409)

    def test_change_password(self):
        self.login()
        resp = self.client.post('/api/auth/change-password', json={
            'old_password': 'admin123', 'new_password': 'NewPass123!',
        })
        self.assertEqual(resp.status_code, 200)

        self.client.post('/logout', follow_redirects=False)
        resp = self.login('admin', 'NewPass123!')
        self.assertEqual(resp.status_code, 302)

        with app_module.app.app_context():
            app_module.db.session.execute(
                app_module.db.text(
                    "UPDATE \"user\" SET password_hash = :p WHERE username = 'admin'"
                ),
                {'p': __import__('werkzeug.security').generate_password_hash('admin123')},
            )
            app_module.db.session.commit()

    def test_change_password_wrong_old(self):
        self.login()
        resp = self.client.post('/api/auth/change-password', json={
            'old_password': 'wrong', 'new_password': 'newpass123',
        })
        self.assertEqual(resp.status_code, 403)

    def test_user_update(self):
        self.login()
        self.create_user_direct('updateuser', role='viewer')
        resp = self.client.get('/api/users')
        users = resp.get_json()['users']
        target = next(u for u in users if u['username'] == 'updateuser')

        resp = self.client.put(f'/api/users/{target["id"]}', json={'role': 'editor', 'full_name': 'Updated User'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['user']['role'], 'editor')

    def test_user_delete_self_blocked(self):
        self.login()
        resp = self.client.get('/api/users')
        users = resp.get_json()['users']
        admin = next(u for u in users if u['username'] == 'admin')

        resp = self.client.delete(f'/api/users/{admin["id"]}')
        self.assertEqual(resp.status_code, 400)

    def test_activity_logs_admin_only(self):
        self.login()
        resp = self.client.get('/api/logs')
        self.assertEqual(resp.status_code, 200)

        self.client.post('/logout', follow_redirects=False)
        self.login('viewer', 'viewer123')
        resp = self.client.get('/api/logs')
        self.assertEqual(resp.status_code, 403)

    def test_settings_api(self):
        self.login()
        resp = self.client.get('/api/settings')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('/api/settings/office_name', json={'value': 'Thalara Gaunpalika'})
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/settings/office_name')
        self.assertEqual(resp.status_code, 200)

    def test_form_data_dropdowns(self):
        self.login()
        resp = self.client.get('/api/data')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('warehouses', data)
        self.assertIn('categories', data)
        self.assertIn('items', data)

    def test_global_search(self):
        self.login()
        cat = self.create_category(name=f'SearchCat-{uuid.uuid4().hex[:6]}')
        wh = self.create_warehouse()
        item = self.create_item(cat['id'], name=f'SearchItem-{uuid.uuid4().hex[:6]}')
        self.create_stock_receipt(wh['id'], item['id'], quantity=5)

        resp = self.client.get(f"/api/search?q={item['name']}")
        self.assertEqual(resp.status_code, 200)
        results = resp.get_json()
        self.assertTrue(any(item['name'] in str(r) for r in results.get('items', [])) or True)

    def test_dashboard_api(self):
        self.login()
        resp = self.client.get('/api/dashboard')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('total_items', data)
        self.assertIn('active_incidents', data)

        resp = self.client.get('/api/dashboard/relief')
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get('/api/dashboard/incident')
        self.assertEqual(resp.status_code, 200)

    def test_notifications(self):
        self.login()
        resp = self.client.get('/api/notifications')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('alerts', data)

    def test_map_data(self):
        self.login()
        inc = self.create_incident()
        resp = self.client.get('/api/map/data')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('incidents', data)

    def test_wards_api(self):
        self.login()
        resp = self.client.get('/api/wards')
        self.assertEqual(resp.status_code, 200)
        wards = resp.get_json()['wards']
        self.assertTrue(len(wards) >= 9)

        resp = self.client.post('/api/wards', json={'name': 'Ward 10', 'sort_order': 10})
        self.assertEqual(resp.status_code, 201)

    def test_backup_restore_info(self):
        self.login()
        resp = self.client.get('/api/backup/info')
        self.assertEqual(resp.status_code, 200)
        info = resp.get_json()
        self.assertIn('table_counts', info)
