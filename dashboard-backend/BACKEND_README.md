# Temacina Dashboard - Backend API

## 🏗️ Architecture Overview

This is a production-grade Django REST Framework backend for user authentication, authorization, and audit logging.

```
dashboard-backend/
├── config/                           # Project settings & core config
│   ├── settings.py                  # Comprehensive production settings
│   ├── urls.py                      # Main URL router with API docs
│   ├── asgi.py                      # Async server gateway
│   ├── wsgi.py                      # WSGI application
│   └── celery.py                    # Celery task queue config
│
├── apps/
│   ├── users/                       # User management
│   │   ├── models.py               # User, Role, UserSession, UserClient
│   │   ├── managers.py             # Custom user creation manager
│   │   ├── permissions.py          # 7 role-based permission classes
│   │   ├── validators.py           # Strong password enforcement
│   │   ├── services/
│   │   │   ├── user.py            # User CRUD business logic
│   │   │   ├── session.py         # Session tracking
│   │   │   └── client.py          # Company assignment
│   │   └── api/
│   │       ├── serializers.py      # 9 DRF serializers
│   │       ├── views.py            # 10 API views
│   │       ├── urls.py             # 11 user endpoints
│   │       └── filters.py          # Advanced filtering
│   │
│   ├── authentication/              # Auth & security
│   │   ├── models.py               # PasswordResetToken (1-hour expiry)
│   │   ├── services.py             # AuthService (login/logout/reset)
│   │   ├── throttles.py            # Rate limiting & lockout
│   │   ├── email.py                # Async password reset emails
│   │   └── api/
│   │       ├── serializers.py       # 3 auth serializers
│   │       ├── views.py             # 5 auth views
│   │       └── urls.py              # 6 auth endpoints
│   │
│   ├── audit/                       # Audit trail
│   │   ├── models.py               # AuditLog (11 action types)
│   │   ├── services.py             # write_log() helper
│   │   ├── middleware.py           # Auto IP detection
│   │   └── admin.py                # Django admin interface
│   │
│   ├── core/                        # Shared utilities
│   │   ├── exceptions.py           # Custom exception handlers
│   │   ├── mixins.py               # Reusable model mixins
│   │   ├── pagination.py           # Standard pagination
│   │   ├── renderers.py            # Custom response renderers
│   │   ├── utils.py                # Helper functions
│   │   └── validators.py           # Input validation
│   │
│   ├── safex/                       # Company/organization data
│   ├── analytics/                   # Usage analytics & reporting
│   ├── reports/                     # Report generation
│   └── notifications/               # User notifications
│
├── .env.example                      # Environment template
├── requirements.txt                  # All dependencies
├── manage.py                         # Django management CLI
├── pytest.ini                        # Testing configuration
├── conftest.py                       # Pytest fixtures
└── README.md                         # This file
```

---

## 🔑 Key Features

### 1. **JWT Authentication** (SimpleJWT)

- Email-based login (not username)
- 15-minute access tokens + 7-day refresh tokens
- Automatic token rotation on refresh
- Blacklist tokens on logout
- Embedded session_id in JWT for request traceability

**Endpoints:**

```
POST   /api/v1/auth/login/              → {"access", "refresh", "user", "session_id"}
POST   /api/v1/auth/logout/             → Blacklist token
POST   /api/v1/auth/refresh/            → New access token
POST   /api/v1/auth/password/change/    → Change own password
POST   /api/v1/auth/password/reset/     → Request reset token (safe endpoint)
POST   /api/v1/auth/password/reset/confirm/  → Confirm reset with token
```

### 2. **Role-Based Access Control (RBAC)**

- 5-tier hierarchy: **viewer** (0) < **analyst** (1) < **manager** (2) < **admin** (3) < **superadmin** (4)
- Privilege hierarchy enforcement on all operations
- Object-level permissions (e.g., managers can only change their direct reports)

**7 Permission Classes:**

```python
IsSuperAdmin              # Only superadmin
IsAdminOrAbove            # Rank >= admin
IsManagerOrAbove          # Rank >= manager
IsAnalystOrAbove          # Rank >= analyst
IsViewer                  # All authenticated users
CanManageUser             # Hierarchical user management
CanAccessCompany          # Company assignment visibility
```

### 3. **Password Security**

- **Minimum 10 characters** with uppercase, lowercase, digit, and special character
- **Bcrypt hashing** via Django's `set_password()`
- Strong password validator with common password checks
- Password change requires old password verification

**Validator Logic:**

```python
# Must contain:
- 10+ characters
- At least 1 uppercase (A-Z)
- At least 1 lowercase (a-z)
- At least 1 digit (0-9)
- At least 1 special character (!@#$%^&*)
- Not a common password (password, qwerty123, admin, etc.)
```

### 4. **Brute-Force Protection**

- **5 login attempts/minute per IP** (rate throttle)
- **15-minute account lockout** after 5 failed attempts
- Redis-backed with TTL (prevents false positives)
- Email enumeration prevented (login always returns consistent response)
- Rate limit on password reset: **3 requests/hour per IP**

**Implementation:**

```python
# Login throttle: AnonRateThrottle('5/min') per IP
# Account lockout: Redis key `login_attempts:{MD5(email)}` with 15min TTL
# After 5 failures: Return 403 "Account locked for 15 minutes"
```

### 5. **Audit Logging**

- Tracks 11 action types: LOGIN, LOGOUT, LOGIN_FAILED, PASSWORD_RESET, USER_CREATED, USER_UPDATED, USER_DELETED, ROLE_CHANGED, COMPANY_VIEWED, DATA_EXPORTED, ACCESS_DENIED
- Records: user_id, action, entity_type, entity_id, details (JSON), IP address, timestamp
- Indexed for fast queries: (user, created_at), (action_type, created_at), (entity_type, entity_id)
- Non-blocking writes (audit failures don't break API)

**Usage:**

```python
from apps.audit.services import write_log
write_log(
    user=request.user,
    action="LOGIN",
    entity_type="User",
    entity_id=request.user.id,
    ip_address=request.META.get('REMOTE_ADDR')
)
```

### 6. **Email Service** (Async via Celery)

- Asynchronous password reset emails via Celery tasks
- 3 automatic retries on failure (60-second delay between retries)
- Supports: Gmail, SendGrid, Mailgun, AWS SES
- Password reset links valid for **1 hour** with one-time use

**Setup:**

```python
# config/settings.py
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "your-email@gmail.com"
EMAIL_HOST_PASSWORD = "app-specific-password"  # Not your main password!
DEFAULT_FROM_EMAIL = "noreply@temacina.com"
FRONTEND_URL = "https://dashboard.temacina.com"
```

### 7. **Password Reset Tokens**

- **SHA-256 hashed** (never store raw tokens)
- **64-character hex** (256-bit entropy)
- **1-hour expiry** with timezone-aware timestamps
- **One-time use** (invalidated after use)
- All previous tokens for user automatically invalidated on new reset request

**Security Flow:**

```
1. User requests reset → Token generated → SHA-256 hash stored
2. Reset link sent with raw token (hash cannot be reversed)
3. User clicks link → Token hash validated → Password changed
4. All user sessions invalidated → Must re-login
```

### 8. **User Management**

- Create users with role assignment
- Update users (non-privileged: self, privileged: admin)
- Soft delete (deactivate users)
- Change roles with hierarchy validation
- Assign companies with duplicate prevention
- Track direct reports (manager hierarchy)
- View login history and sessions

**User Service Methods:**

```python
get_all(filters)              # List users with filtering
get_by_id(user_id)            # Get with Redis caching (300s TTL)
create_user(user, data)       # Create with privilege checks
update_user(actor, target, data)  # Role-based updates
deactivate_user(actor, target)    # Soft delete
change_role(actor, target, role)  # Hierarchy validation
assign_company(user, company_id)  # Company assignment
get_direct_reports(user_id)   # Manager tree
get_assigned_companies(user_id)   # Company list
```

### 9. **Caching**

- User profiles cached for 300 seconds (Redis)
- Account lockout tracking with 15-minute TTL
- Session storage in cache (configurable expiry: 1 hour idle)
- Automatic cache invalidation on user updates

```python
# Key formats:
user:profile:{user_id}            # 300s TTL
login_attempts:{MD5(email)}       # 900s (15min) TTL
django.contrib.sessions.*         # 3600s (1hr) TTL
```

### 10. **Security Hardening**

All settings in `config/settings.py`:

**HTTPS & Transport Security:**

- `SECURE_SSL_REDIRECT = True` (redirects HTTP → HTTPS in production)
- `SESSION_COOKIE_SECURE = True` (cookies only over HTTPS)
- `CSRF_COOKIE_SECURE = True` (CSRF token only over HTTPS)
- `SECURE_HSTS_SECONDS = 31536000` (1 year HSTS header)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`

**Cookie Security:**

- `SESSION_COOKIE_HTTPONLY = True` (no JavaScript access)
- `SESSION_COOKIE_SAMESITE = "Strict"` (prevents CSRF)
- `SESSION_COOKIE_AGE = 3600` (1-hour idle timeout)

**Content Security:**

- `SECURE_BROWSER_XSS_FILTER = True`
- `SECURE_CONTENT_SECURITY_POLICY` (CSP headers)
- `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`

**CORS Configuration:**

```python
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "https://dashboard.temacina.com"]
CORS_ALLOW_CREDENTIALS = True
CORS_MAX_AGE = 86400  # 24 hours
```

---

## 📊 Database Schema

### Core Tables (managed=False - Neon only)

```sql
-- User hierarchy
users
├── id (PK)
├── first_name, last_name, email (unique), phone
├── password_hash
├── role_id (FK → roles)
├── sector_id (FK → user_sectors)
├── manager_id (FK → users, nullable)
└── is_active, created_at

-- Session tracking
user_sessions
├── id (PK)
├── user_id (FK → users)
├── login_at, logout_at
├── ip_address, user_agent
└── is_active

-- Company assignments (cross-app)
user_clients
├── id (PK)
├── user_id (FK → users)
├── company_id (FK → companies in safex app)
└── assigned_at

-- Reference data
roles (id, name: superadmin|admin|manager|analyst|viewer)
user_sectors (id, name)
```

### Managed Tables (Django migrations)

```sql
-- Password reset tokens (one-time use)
password_reset_tokens
├── id (PK)
├── user_id (FK → users)
├── token_hash (unique, SHA-256)
├── created_at, expires_at
├── used_at (nullable)
└── custom save() enforces 1-hour expiry
```

### Audit Tables

```sql
-- Immutable audit trail
audit_logs
├── id (PK)
├── user_id (FK → users, nullable)
├── action_type (LOGIN|LOGOUT|LOGIN_FAILED|etc)
├── entity_type, entity_id
├── details (JSON)
├── ip_address
└── created_at (indexed)
```

---

## 🚀 Installation & Setup

### 1. Clone & Install Dependencies

```bash
cd dashboard-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values:
# - SECRET_KEY (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# - DATABASE_URL (Neon PostgreSQL connection)
# - EMAIL_HOST_USER / EMAIL_HOST_PASSWORD
# - FRONTEND_URL
# - REDIS_URL
```

### 3. Create Database Tables (Manual - Run in Neon SQL Editor First)

```sql
-- See SETUP_GUIDE.md for full SQL DDL
-- Tables: roles, user_sectors, users, user_sessions, user_clients, audit_logs
```

### 4. Run Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser --email admin@temacina.com
```

### 6. Start Services

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat (optional, for scheduled tasks)
celery -A config beat -l info

# Terminal 4: Redis (if not running via Docker)
redis-server
```

### 7. Access API Documentation

- **Swagger UI:** http://localhost:8000/api/docs/swagger/
- **ReDoc:** http://localhost:8000/api/docs/redoc/
- **Django Admin:** http://localhost:8000/admin/

---

## 🧪 Testing

### Run All Tests

```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov                    # Coverage report
pytest -k "test_login"          # Run specific test
```

### Test Authentication Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@temacina.com","password":"YourPassword123!"}'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "session_id": 1,
#   "user": {"id": 1, "full_name": "Admin", "email": "...", "role": "superadmin"}
# }

# 2. Access protected endpoint
curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer {access_token}"

# 3. Logout
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"{refresh_token}"}'
```

---

## 📡 API Endpoints

### Authentication (6 endpoints)

```
POST   /api/v1/auth/login/                 Login
POST   /api/v1/auth/logout/                Logout
POST   /api/v1/auth/refresh/               Refresh token
POST   /api/v1/auth/password/change/       Change password
POST   /api/v1/auth/password/reset/        Request reset
POST   /api/v1/auth/password/reset/confirm/  Confirm reset
```

### User Management (11 endpoints)

```
GET    /api/v1/users/me/                   Own profile
PATCH  /api/v1/users/me/                   Update profile
GET    /api/v1/users/                      List users (Admin+)
POST   /api/v1/users/                      Create user (Admin+)
GET    /api/v1/users/roles/                List roles
GET    /api/v1/users/sectors/              List sectors
GET    /api/v1/users/{id}/                 User detail (Manager+)
PATCH  /api/v1/users/{id}/                 Update user (Admin+)
DELETE /api/v1/users/{id}/                 Deactivate user (Admin+)
POST   /api/v1/users/{id}/role/            Change role (Admin+)
GET    /api/v1/users/{id}/reports/         Direct reports
GET    /api/v1/users/{id}/sessions/        Login history
GET    /api/v1/users/{id}/companies/       Assigned companies
POST   /api/v1/users/{id}/companies/assign/  Assign company (Admin+)
```

### Documentation

```
GET    /api/v1/schema/                     OpenAPI schema
GET    /api/docs/swagger/                  Swagger UI
GET    /api/docs/redoc/                    ReDoc UI
```

---

## 🔒 Security Checklist

Before deploying to production:

- [ ] Set `DEBUG = False` in .env
- [ ] Generate strong `SECRET_KEY` (min 50 chars, random)
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Enable SSL/HTTPS: `SECURE_SSL_REDIRECT = True`
- [ ] Configure secure cookies: `SESSION_COOKIE_SECURE = True`
- [ ] Set up database backups (Neon automatic backups)
- [ ] Enable database SSL connections
- [ ] Configure email credentials (Gmail app-specific password)
- [ ] Set up Redis with authentication
- [ ] Enable CORS only for your frontend domain
- [ ] Configure rate limiting thresholds
- [ ] Set up monitoring/logging (Sentry, LogRocket)
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Test password reset email flow
- [ ] Test brute-force lockout (5 failed logins)
- [ ] Verify JWT token expiry
- [ ] Test token refresh workflow
- [ ] Verify audit logging

---

## 🐛 Troubleshooting

### Module Not Found

```bash
pip install -r requirements.txt
```

### Database Connection Error

```
Check DATABASE_URL in .env
Verify Neon credentials and IP whitelist
```

### Email Not Sending

```
Check EMAIL_HOST_USER/PASSWORD in .env
For Gmail: Use app-specific password (not main password)
Check FRONTEND_URL is set correctly
```

### Redis Connection Failed

```
Ensure Redis is running: redis-server
Check REDIS_URL in .env
```

### Celery Tasks Not Executing

```
Start Celery worker: celery -A config worker -l info
Check task logs for errors
```

### JWT Token Invalid

```
Verify token hasn't expired (15 min lifetime)
Check SECRET_KEY hasn't changed
Clear token cache if using custom token storage
```

---

## 📚 References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [OWASP Security Guidelines](https://owasp.org/)

---

## 📝 License

Proprietary - Temacina Dashboard

---

**Last Updated:** June 2026  
**Status:** Production Ready ✅
