# Authorization System Implementation Plan

## 1. Analysis of Current State

**Current "authorization":**
- No user database, no authentication, no roles
- A hardcoded `UNLOCK_KEY` (default: `admin123`) frontend-only unlock mechanism
- `is_locked` boolean fields on models used as edit/delete gating
- Anyone can hit API endpoints and modify data if they know the unlock key

**Security gaps:**
- `is_locked` check is frontend-centric (disable inputs) but backend does enforce it for some routes
- No audit trail of *who* made changes
- No differentiated access levels

---

## 2. Recommended System: Role-Based Access Control (RBAC)

**Roles:**
| Role | Permissions |
|------|-------------|
| `admin` | CRUD on everything, user management, settings |
| `editor` | CRUD on most records; can view funds summary but not create expenditures |
| `viewer` | Read-only on all public/important data |

**Libraries to add:**
- `Flask-Login` (session management, `@login_required`)
- No Flask-Principal needed; lightweight custom decorators are enough for this app

---

## 3. Database Changes

### 3.1 Add new models (in `app.py`)

```
User {
  id: int PK
  username: str unique
  password_hash: str
  role: str (default='viewer')  # admin | operator | finance | viewer
  full_name: str (optional)
  is_active: bool (default=True)
  created_at: datetime
  last_login: datetime (nullable)
}
```

- Password hashing via `werkzeug.security.generate_password_hash` / `check_password_hash`
- Seed an initial admin user during migration (username: `admin`, password from env `ADMIN_PASSWORD`, or `admin123` in dev)
- Seed one default `operator` and one `viewer` if desired

### 3.2 Migration approach for existing DB

Because project uses SQLite, add an `upgrade_auth()` function in `init_db()` that:
1. Checks if `user` table exists
2. Creates it if missing
3. Seeds default users (only if table was just created - avoid duplicates)

ALSO, existing users should still keep working while authorization is being implemented (grace period). We should NOT remove the old lock endpoints immediately—we deprecate them.

---

## 4. Code Changes

### 4.1 Auth module
- Add `auth_helpers.py` with decorators:
  - `@login_required` — redirect to login if not authenticated (wrap route)
  - `@role_required(*roles)` — allow only specific roles
  - `@permission_required(action)` — map actions (create/update/delete/view) to roles
- Support both HTML view routes and JSON API routes

### 4.2 Login/Logout routes
- `POST /api/auth/login` → sets session cookie
- `POST /api/auth/logout` → clears session
- `GET /api/auth/me` → returns current user info (`current_user`)
- `POST /api/auth/change-password`

### 4.3 Protect routes
- Replace manual `is_locked` key verification with role checks
- `is_locked` becomes optional "review/audit lock" flag still enforced by `@permission_required('edit')`
- All current endpoints get wrapped:
  - `GET /api/funds/summary` → `@login_required` (+ finance or admin for sensitive amounts, optional)
  - `POST /api/funds/transactions` → `@role_required('admin', 'finance')`
  - `GET/POST /api/distributions` → `@login_required`
  - `PUT/DELETE /api/distributions/<id>` → `@role_required('admin', 'operator')`
  - Same pattern for disasters, event-logs, situation-reports, public-information, ssf-beneficiaries, inventory

### 4.4 Remove old unlock-key endpoints
- Remove `/api/verify-unlock-key`
- Remove `/api/distributions/<id>/lock`, `/api/disasters/<id>/lock`, etc. — *or* keep them but replace internal `UNLOCK_KEY` check with role check
- Update templates to remove unlock-key prompts (form.html, disaster_report.html, settings.html)
- Frontend unlocks are no longer needed because role-based access controls who sees edit forms

### 4.5 Template changes
- Add login modal or login page (simplest: a top-bar "Sign In" button -> modal)
- Show current logged-in user + logout in nav
- Hide/disable forms based on user role (e.g., viewers never see Delete buttons)
- Remove all `admin123` / unlock-key related JavaScript

---

## 5. Settings & Management

- Add `/api/users` endpoints for user management (admin only):
  - `GET /api/users` → list users
  - `POST /api/users` → create user
  - `PUT /api/users/<id>` → update user role
  - `DELETE /api/users/<id>` → deactivate user
- Frontend: simple user management table in `settings.html` under a new tab

---

## 6. Files to modify

| File | Changes |
|------|---------|
| `app.py` | Add `User` model, auth routes, decorators, protect existing routes, remove unlock-key logic, seed default users |
| `requirements.txt` | Add `Flask-Login==0.6.3` |
| `templates/base.html` | Add login/logout UI |
| `templates/form.html` | Remove unlock-key JS, hide edit controls based on role |
| `templates/disaster_report.html` | Remove unlock-key JS |
| `templates/settings.html` | Add user management section |
| `templates/*.html` (others with lock buttons) | Remove lock/unlock buttons, replace with role-based visibility |

---

## 7. Implementation order

1. Add `User` model + auth helpers
2. Add login/logout endpoints + login template
3. Protect all existing routes with `@login_required` / role decorators
4. Remove unlock-key endpoints and hardcoded key references
5. Update settings page for user management
6. Template cleanup (remove unlock/lock UI)
7. Users without account can see dashboard without any role and permissions but cannot perform any operations 
---

