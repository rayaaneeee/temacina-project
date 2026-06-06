# Dashboard Backend — Complete Implementation Roadmap (A → Z) (was completed except last step (docker step))

> Follow every step in order. Each phase produces working, testable code before moving on.  
> **Never skip a phase.** Later phases depend on earlier ones compiling and passing tests.

---

## PHASE 0 — Local Environment & Tooling

### Step 0.1 — Python & Virtual Environment

```bash
python --version          # Must be 3.11+
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
```

### Step 0.2 — Project Initialization

```bash
mkdir dashboard-backend && cd dashboard-backend
git init
pip install Django==5.0.6
django-admin startproject config .
```

### Step 0.3 — Create the Full Directory Skeleton

```bash
# Apps
mkdir -p apps/{authentication,users,analytics,reports,audit,notifications}
for app in authentication users analytics reports audit notifications; do
  mkdir -p apps/$app/{api,tests}
  touch apps/$app/__init__.py apps/$app/models.py apps/$app/admin.py \
        apps/$app/services.py apps/$app/apps.py \
        apps/$app/api/__init__.py apps/$app/api/views.py \
        apps/$app/api/serializers.py apps/$app/api/urls.py \
        apps/$app/tests/__init__.py apps/$app/tests/test_models.py \
        apps/$app/tests/test_services.py apps/$app/tests/test_views.py
done

# Core (shared utilities)
mkdir -p core
touch core/__init__.py core/exceptions.py core/pagination.py \
      core/renderers.py core/mixins.py core/validators.py core/utils.py

# Config settings split
mkdir -p config/settings
touch config/settings/__init__.py config/settings/base.py \
      config/settings/development.py config/settings/production.py \
      config/settings/testing.py

# Requirements split
mkdir -p requirements
touch requirements/base.txt requirements/development.txt requirements/production.txt

# Infrastructure
mkdir -p infrastructure/{docker,nginx}
touch infrastructure/docker/Dockerfile \
      infrastructure/docker/Dockerfile.celery \
      infrastructure/docker/entrypoint.sh \
      infrastructure/nginx/nginx.conf \
      infrastructure/docker-compose.yml

# Scripts & root files
mkdir -p scripts
touch scripts/seed_data.py scripts/healthcheck.py
touch .env .env.example .gitignore pytest.ini manage.py
```

### Step 0.4 — .gitignore

```gitignore
.venv/
__pycache__/
*.pyc
*.pyo
.env
*.sqlite3
staticfiles/
mediafiles/
.coverage
htmlcov/
dist/
*.egg-info/
.DS_Store
```

### Step 0.5 — .env & .env.example

```env
# .env (never commit this file)
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=True

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=dashboard_db
DB_USER=dashboard_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Security (production only)
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdashboard.com

# Sentry (production only)
SENTRY_DSN=
```

---

## PHASE 1 — Requirements & Dependencies

### Step 1.1 — requirements/base.txt

```
Django==5.0.6
djangorestframework==3.15.2
django-cors-headers==4.4.0
django-filter==24.2
psycopg2-binary==2.9.9
redis==5.0.7
django-redis==5.4.0
hiredis==3.0.0
djangorestframework-simplejwt==5.3.1
django-ratelimit==4.1.0
celery==5.4.0
django-celery-beat==2.6.0
django-celery-results==2.5.1
flower==2.0.1
python-decouple==3.8
Pillow==10.3.0
gunicorn==22.0.0
sentry-sdk==2.5.1
django-structlog==8.1.0
django-health-check==3.18.3
pydantic==2.7.1
```

### Step 1.2 — requirements/development.txt

```
-r base.txt
pytest==8.2.2
pytest-django==4.8.0
pytest-cov==5.0.0
factory-boy==3.3.0
Faker==25.3.0
django-debug-toolbar==4.4.1
ipython==8.25.0
```

### Step 1.3 — requirements/production.txt

```
-r base.txt
whitenoise==6.7.0
django-storages==1.14.3
boto3==1.34.130
```

### Step 1.4 — Install & Verify

```bash
pip install -r requirements/development.txt
python -c "import django; print(django.__version__)"  # must print 5.0.6
```

---

## PHASE 2 — Settings Architecture

### Step 2.1 — config/settings/base.py

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# ── Apps ──────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "django_celery_beat",
    "django_celery_results",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.contrib.celery",
]

LOCAL_APPS = [
    "apps.authentication",
    "apps.users",
    "apps.analytics",
    "apps.reports",
    "apps.audit",
    "apps.notifications",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ── Middleware ────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
    "apps.audit.middleware.AuditLogMiddleware",   # custom — added in Phase 8
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ── Database ──────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE":   config("DB_ENGINE"),
        "NAME":     config("DB_NAME"),
        "USER":     config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST":     config("DB_HOST"),
        "PORT":     config("DB_PORT"),
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",
        },
        "CONN_MAX_AGE": 60,
    }
}

# ── Cache (Redis) ─────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PARSER_CLASS": "redis.connection.HiredisParser",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50},
        },
        "KEY_PREFIX": "dashboard",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ── Auth ──────────────────────────────────────────────────
AUTH_USER_MODEL = "users.User"   # custom user — defined in Phase 5

# ── DRF ──────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "core.renderers.StandardJSONRenderer",       # Phase 3
    ],
    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "core.exceptions.global_exception_handler",  # Phase 3
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# ── JWT ───────────────────────────────────────────────────
from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "UPDATE_LAST_LOGIN": True,
}

# ── Celery ────────────────────────────────────────────────
CELERY_BROKER_URL        = config("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND    = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/2")
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE          = "UTC"
CELERY_BEAT_SCHEDULER    = "django_celery_beat.schedulers:DatabaseScheduler"

# ── Static / Media ────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "mediafiles"

# ── Internationalization ──────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Logging ───────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "django_structlog.formatter.StructlogFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
```

### Step 2.2 — config/settings/development.py

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE  = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]

# Relaxed CORS for local frontend dev
CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### Step 2.3 — config/settings/production.py

```python
from .base import *

DEBUG = False

# Security hardening
SECURE_SSL_REDIRECT             = True
SECURE_HSTS_SECONDS             = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS  = True
SECURE_HSTS_PRELOAD             = True
SECURE_PROXY_SSL_HEADER         = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE           = True
CSRF_COOKIE_SECURE              = True
X_FRAME_OPTIONS                 = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF     = True
SECURE_BROWSER_XSS_FILTER       = True

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="").split(",")

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

import sentry_sdk
sentry_sdk.init(dsn=config("SENTRY_DSN", default=""), traces_sample_rate=0.2)
```

### Step 2.4 — config/settings/testing.py

```python
from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

CELERY_TASK_ALWAYS_EAGER = True   # run tasks synchronously in tests
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
```

### Step 2.5 — pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
python_files = tests/test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --tb=short -v
```

### Step 2.6 — Verify Settings Load

```bash
python manage.py check --settings=config.settings.development
```

---

## PHASE 3 — Core Utilities (Shared Layer)

> Build this before any app. Every app imports from `core/`.

### Step 3.1 — core/renderers.py

```python
from rest_framework.renderers import JSONRenderer
import json

class StandardJSONRenderer(JSONRenderer):
    """Wraps every response in { success, data, meta, errors }."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200
        success = 200 <= status_code < 400

        # DRF errors arrive as dict with 'detail' or field names
        if not success:
            payload = {"success": False, "data": None, "errors": data}
        else:
            payload = {"success": True, "data": data, "errors": None}

        return super().render(payload, accepted_media_type, renderer_context)
```

### Step 3.2 — core/exceptions.py

```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def global_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response  # DRF already handled it; renderer wraps it

    # Unhandled exception — log and return 500
    logger.exception("Unhandled exception", exc_info=exc)
    return Response(
        {"detail": "An internal error occurred. Our team has been notified."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
```

### Step 3.3 — core/pagination.py

```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsPagination(PageNumberPagination):
    page_size              = 20
    page_size_query_param  = "page_size"
    max_page_size          = 200

    def get_paginated_response(self, data):
        return Response({
            "success": True,
            "data": data,
            "meta": {
                "page":       self.page.number,
                "page_size":  self.get_page_size(self.request),
                "total":      self.page.paginator.count,
                "total_pages":self.page.paginator.num_pages,
                "next":       self.get_next_link(),
                "previous":   self.get_previous_link(),
            },
            "errors": None,
        })
```

### Step 3.4 — core/mixins.py

```python
from rest_framework.response import Response
from rest_framework import status

class CreateMixin:
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SoftDeleteMixin:
    """For models with an `is_active` field instead of hard deletes."""
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### Step 3.5 — core/utils.py

```python
import hashlib, uuid

def generate_cache_key(*args) -> str:
    raw = ":".join(str(a) for a in args)
    return hashlib.md5(raw.encode()).hexdigest()

def generate_uuid() -> str:
    return str(uuid.uuid4())
```

---

## PHASE 4 — Root URL Configuration

### Step 4.1 — config/urls.py

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/",    admin.site.urls),
    path("api/health/", include("health_check.urls")),
    path("api/v1/auth/",          include("apps.authentication.api.urls")),
    path("api/v1/users/",         include("apps.users.api.urls")),
    path("api/v1/analytics/",     include("apps.analytics.api.urls")),
    path("api/v1/reports/",       include("apps.reports.api.urls")),
    path("api/v1/notifications/", include("apps.notifications.api.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
```

---

## PHASE 5 — Users App (Custom Auth Model)

> **Must be done before any migration.** Changing AUTH_USER_MODEL after the first migration is painful.

### Step 5.1 — apps/users/models.py

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN    = "admin",    "Admin"
        MANAGER  = "manager",  "Manager"
        ANALYST  = "analyst",  "Analyst"
        VIEWER   = "viewer",   "Viewer"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email      = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name  = models.CharField(max_length=150, blank=True)
    role       = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = UserManager()

    class Meta:
        db_table   = "users"
        ordering   = ["-created_at"]
        indexes    = [models.Index(fields=["email", "is_active"])]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
```

### Step 5.2 — apps/users/apps.py

```python
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    label = "users"
```

### Step 5.3 — apps/users/permissions.py

```python
from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class IsManagerOrAbove(BasePermission):
    ALLOWED = {"admin", "manager"}
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED

class IsAnalystOrAbove(BasePermission):
    ALLOWED = {"admin", "manager", "analyst"}
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in self.ALLOWED
```

### Step 5.4 — apps/users/services.py

```python
from django.core.cache import cache
from .models import User

CACHE_TTL = 300  # 5 minutes

class UserService:
    @staticmethod
    def get_by_id(user_id: str) -> User | None:
        key = f"user:{user_id}"
        cached = cache.get(key)
        if cached:
            return cached
        try:
            user = User.objects.get(id=user_id, is_active=True)
            cache.set(key, user, CACHE_TTL)
            return user
        except User.DoesNotExist:
            return None

    @staticmethod
    def invalidate_cache(user_id: str):
        cache.delete(f"user:{user_id}")
```

### Step 5.5 — apps/users/api/serializers.py

```python
from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role",
                  "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["first_name", "last_name", "role"]
```

### Step 5.6 — apps/users/api/views.py

```python
from rest_framework import generics, permissions
from apps.users.models import User
from apps.users.api.serializers import UserSerializer, UserUpdateSerializer
from apps.users.permissions import IsAdmin

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    search_fields  = ["email", "first_name", "last_name"]
    filterset_fields = ["role", "is_active"]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
```

### Step 5.7 — apps/users/api/urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    path("me/",       views.MeView.as_view(),        name="user-me"),
    path("",          views.UserListView.as_view(),   name="user-list"),
    path("<uuid:pk>/",views.UserDetailView.as_view(), name="user-detail"),
]
```

### Step 5.8 — Run First Migration

```bash
python manage.py makemigrations users
python manage.py migrate
python manage.py createsuperuser
```

---

## PHASE 6 — Authentication App (JWT)

### Step 6.1 — apps/authentication/services.py

```python
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> dict | None:
        user = authenticate(username=email, password=password)
        if not user or not user.is_active:
            return None
        refresh = RefreshToken.for_user(user)
        return {
            "access":  str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id":    str(user.id),
                "email": user.email,
                "role":  user.role,
            },
        }

    @staticmethod
    def logout(refresh_token: str) -> bool:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False
```

### Step 6.2 — apps/authentication/api/serializers.py

```python
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
```

### Step 6.3 — apps/authentication/api/views.py

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import LoginSerializer, LogoutSerializer, ChangePasswordSerializer
from apps.authentication.services import AuthService

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = AuthService.login(**serializer.validated_data)
        if not tokens:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.logout(serializer.validated_data["refresh"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Old password incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated."})
```

### Step 6.4 — apps/authentication/api/urls.py

```python
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("login/",           views.LoginView.as_view(),          name="auth-login"),
    path("logout/",          views.LogoutView.as_view(),         name="auth-logout"),
    path("refresh/",         TokenRefreshView.as_view(),         name="auth-refresh"),
    path("password/change/", views.ChangePasswordView.as_view(), name="auth-change-password"),
]
```

### Step 6.5 — Test Auth Manually

```bash
python manage.py runserver
# POST http://localhost:8000/api/v1/auth/login/
# Body: { "email": "admin@test.com", "password": "your_password" }
```

---

## PHASE 7 — Celery Setup

### Step 7.1 — config/celery.py

```python
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("dashboard")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
```

### Step 7.2 — config/**init**.py

```python
from .celery import app as celery_app
__all__ = ("celery_app",)
```

### Step 7.3 — Verify Celery

```bash
# Terminal 1: Redis
docker run -p 6379:6379 redis

# Terminal 2: Celery worker
celery -A config worker -l info

# Terminal 3: Celery beat (scheduler)
celery -A config beat -l info
```

---

## PHASE 8 — Audit App (Security Logging)

### Step 8.1 — apps/audit/models.py

```python
from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                   on_delete=models.SET_NULL, related_name="audit_logs")
    action     = models.CharField(max_length=50)
    resource   = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=36, blank=True)
    status     = models.PositiveSmallIntegerField()
    timestamp  = models.DateTimeField(auto_now_add=True, db_index=True)
    extra      = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes  = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
        ]
```

### Step 8.2 — apps/audit/middleware.py

```python
import uuid
from .models import AuditLog

SKIP_PATHS = {"/api/health/", "/static/", "/media/"}

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(p) for p in SKIP_PATHS):
            return self.get_response(request)

        request.request_id = str(uuid.uuid4())
        response = self.get_response(request)

        user = request.user if request.user.is_authenticated else None
        AuditLog.objects.create(
            user       = user,
            action     = request.method,
            resource   = request.path,
            ip_address = self._get_ip(request),
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:500],
            request_id = request.request_id,
            status     = response.status_code,
        )
        return response

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
```

### Step 8.3 — Migrate Audit

```bash
python manage.py makemigrations audit
python manage.py migrate
```

---

## PHASE 9 — Analytics App

### Step 9.1 — apps/analytics/models.py

```python
from django.db import models
from django.conf import settings

class Metric(models.Model):
    name       = models.CharField(max_length=100, db_index=True)
    value      = models.DecimalField(max_digits=18, decimal_places=4)
    unit       = models.CharField(max_length=30, blank=True)
    period     = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta       = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table        = "metrics"
        unique_together = [["name", "period"]]
        ordering        = ["-period"]
        indexes         = [models.Index(fields=["name", "period"])]
```

### Step 9.2 — apps/analytics/cache.py

```python
from django.core.cache import cache

DASHBOARD_METRICS_TTL = 300   # 5 min

def get_dashboard_cache_key(user_id: str) -> str:
    return f"dashboard:metrics:{user_id}"

def invalidate_dashboard_cache(user_id: str):
    cache.delete(get_dashboard_cache_key(user_id))
```

### Step 9.3 — apps/analytics/services.py

```python
from django.core.cache import cache
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Metric
from .cache import get_dashboard_cache_key, DASHBOARD_METRICS_TTL

class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics(user) -> dict:
        key    = get_dashboard_cache_key(str(user.id))
        cached = cache.get(key)
        if cached:
            return cached

        now   = timezone.now().date()
        since = now - timedelta(days=30)

        data = {
            "period": {"from": str(since), "to": str(now)},
            "summary": Metric.objects.filter(period__range=[since, now]).aggregate(
                total_value=Sum("value"),
                avg_value=Avg("value"),
                count=Count("id"),
            ),
        }
        cache.set(key, data, DASHBOARD_METRICS_TTL)
        return data
```

### Step 9.4 — apps/analytics/tasks.py

```python
from celery import shared_task
from .cache import invalidate_dashboard_cache
from apps.users.models import User

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_dashboard_metrics(self):
    """Invalidate all user dashboard caches — run every 5 minutes via Celery Beat."""
    for user in User.objects.filter(is_active=True).values_list("id", flat=True):
        invalidate_dashboard_cache(str(user))
```

### Step 9.5 — apps/analytics/api/views.py

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from apps.analytics.services import AnalyticsService

class DashboardMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.get_dashboard_metrics(request.user)
        return Response(data)
```

### Step 9.6 — apps/analytics/api/urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    path("metrics/", views.DashboardMetricsView.as_view(), name="dashboard-metrics"),
]
```

### Step 9.7 — Migrate Analytics

```bash
python manage.py makemigrations analytics
python manage.py migrate
```

---

## PHASE 10 — Reports App

### Step 10.1 — apps/reports/models.py

```python
from django.db import models
from django.conf import settings
import uuid

class Report(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        PROCESSING = "processing", "Processing"
        READY      = "ready",      "Ready"
        FAILED     = "failed",     "Failed"

    class Format(models.TextChoices):
        PDF   = "pdf",   "PDF"
        EXCEL = "excel", "Excel"
        CSV   = "csv",   "CSV"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="reports")
    title      = models.CharField(max_length=255)
    status     = models.CharField(max_length=20, choices=Status.choices,
                                  default=Status.PENDING, db_index=True)
    format     = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    file       = models.FileField(upload_to="reports/%Y/%m/", null=True, blank=True)
    error_msg  = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reports"
        ordering = ["-created_at"]
```

### Step 10.2 — apps/reports/tasks.py

```python
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_report(self, report_id: str):
    from .models import Report

    try:
        report = Report.objects.get(id=report_id)
        report.status = Report.Status.PROCESSING
        report.save(update_fields=["status"])

        # ── Replace with real generation logic ──
        # e.g. use reportlab for PDF, openpyxl for Excel
        logger.info("Generating report %s", report_id)

        report.status = Report.Status.READY
        report.save(update_fields=["status", "updated_at"])
    except Exception as exc:
        report.status    = Report.Status.FAILED
        report.error_msg = str(exc)
        report.save(update_fields=["status", "error_msg"])
        raise self.retry(exc=exc)
```

### Step 10.3 — apps/reports/api/views.py

```python
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ReportSerializer
from apps.reports.models import Report
from apps.reports.tasks import generate_report

class ReportListCreateView(generics.ListCreateAPIView):
    serializer_class   = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        report = serializer.save(owner=self.request.user)
        generate_report.delay(str(report.id))   # async Celery task


class ReportDetailView(generics.RetrieveDestroyAPIView):
    serializer_class   = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(owner=self.request.user)
```

### Step 10.4 — Migrate Reports

```bash
python manage.py makemigrations reports
python manage.py migrate
```

---

## PHASE 11 — Notifications App

### Step 11.1 — apps/notifications/models.py

```python
from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    class Type(models.TextChoices):
        INFO    = "info",    "Info"
        WARNING = "warning", "Warning"
        ERROR   = "error",   "Error"
        SUCCESS = "success", "Success"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="notifications")
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    type       = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
```

### Step 11.2 — apps/notifications/tasks.py

```python
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_email_notification(user_id: str, subject: str, message: str):
    from apps.users.models import User
    user = User.objects.get(id=user_id)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
```

---

## PHASE 12 — Testing Suite

### Step 12.1 — Factory Classes (apps/users/tests/factories.py)

```python
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.users.models import User

fake = Faker()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email      = factory.LazyAttribute(lambda _: fake.unique.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name  = factory.LazyAttribute(lambda _: fake.last_name())
    password   = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active  = True
    role       = User.Role.ANALYST
```

### Step 12.2 — Example View Test (apps/authentication/tests/test_views.py)

```python
import pytest
from django.urls import reverse
from apps.users.tests.factories import UserFactory

@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, client):
        user = UserFactory(email="test@example.com")
        user.set_password("strongpass123")
        user.save()

        url  = reverse("auth-login")
        resp = client.post(url, {"email": "test@example.com",
                                 "password": "strongpass123"},
                           content_type="application/json")
        assert resp.status_code == 200
        assert "access" in resp.json()["data"]

    def test_login_wrong_password(self, client):
        url  = reverse("auth-login")
        resp = client.post(url, {"email": "x@x.com", "password": "wrong"},
                           content_type="application/json")
        assert resp.status_code in (400, 401)
```

### Step 12.3 — Run Tests

```bash
pytest --cov=apps --cov-report=html
open htmlcov/index.html   # review coverage report
```

---

#### SKIP PHASE 13 FOR NOW

## PHASE 13 — Docker & Infrastructure

### Step 13.1 — infrastructure/docker/Dockerfile

```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements/production.txt .
RUN pip install --no-cache-dir -r production.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000

COPY infrastructure/docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

### Step 13.2 — infrastructure/docker/entrypoint.sh

```bash
#!/bin/sh
set -e
python manage.py migrate --noinput
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Step 13.3 — infrastructure/docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru

  api:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile
    env_file: ../../.env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    ports:
      - "8000:8000"

  worker:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.celery
    env_file: ../../.env
    depends_on: [db, redis]
    command: celery -A config worker -l info -c 4

  beat:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.celery
    env_file: ../../.env
    depends_on: [db, redis]
    command: celery -A config beat -l info

  flower:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.celery
    env_file: ../../.env
    depends_on: [redis]
    ports:
      - "5555:5555"
    command: celery -A config flower --port=5555

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ../../staticfiles:/static:ro
    depends_on: [api]

volumes:
  postgres_data:
```

### Step 13.4 — infrastructure/nginx/nginx.conf

```nginx
events { worker_connections 1024; }

http {
    upstream django {
        server api:8000;
    }

    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate     /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/private/key.pem;
        ssl_protocols       TLSv1.2 TLSv1.3;

        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        location /static/ {
            alias /static/;
            expires 30d;
        }

        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass         http://django;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## PHASE 14 — Final Verification & Go-Live Checklist

```bash
# 1. Full test suite (must be 0 failures)
pytest --cov=apps

# 2. Security checks
python manage.py check --deploy --settings=config.settings.production

# 3. Build and start all containers
cd infrastructure
docker-compose up --build

# 4. Run migrations inside container
docker-compose exec api python manage.py migrate

# 5. Health check
curl https://yourdomain.com/api/health/

# 6. Smoke test auth flow
curl -X POST https://yourdomain.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yourdomain.com","password":"yourpassword"}'
```

### Final Go-Live Checklist

- [ ] All env vars set in production environment (no hardcoded secrets)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` set explicitly
- [ ] SSL certificate installed and working
- [ ] All migrations applied
- [ ] Static files collected
- [ ] Redis reachable from API container
- [ ] Celery worker + beat running and processing tasks
- [ ] Flower monitoring accessible (internal network only)
- [ ] Sentry DSN configured and receiving test events
- [ ] `/api/health/` returns 200 with all checks green
- [ ] Rate limiting active (test with repeated requests)
- [ ] Admin URL changed from `/admin/` to something obscure
- [ ] Nginx access logs streaming
- [ ] Database backups scheduled

---

## Summary: Implementation Timeline

| Phase | What You Build                                    | Blocker For                |
| ----- | ------------------------------------------------- | -------------------------- |
| 0     | Folder scaffold, .env, git                        | Everything                 |
| 1     | Requirements files                                | Package availability       |
| 2     | Settings (base/dev/prod/test)                     | DB connection, all apps    |
| 3     | Core utilities (renderer, exceptions, pagination) | All API responses          |
| 4     | Root URL config                                   | All endpoints              |
| 5     | Users app + custom User model                     | **First migration** · Auth |
| 6     | Authentication app (JWT)                          | All protected endpoints    |
| 7     | Celery + Redis setup                              | All async tasks            |
| 8     | Audit middleware + model                          | Security logging           |
| 9     | Analytics app                                     | Dashboard data             |
| 10    | Reports app                                       | Export features            |
| 11    | Notifications app                                 | Alerts & emails            |
| 12    | Full test suite                                   | Confidence to deploy       |
| 13    | Docker + Nginx                                    | Production deployment      |
| 14    | Verification & go-live                            | Launch                     |

```

```
