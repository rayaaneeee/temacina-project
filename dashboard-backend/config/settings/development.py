from .base import *
import psycopg2.extras
import psycopg2

# Disable psycopg2 native JSON parsing so Django's JSONField can handle it
psycopg2.extras.register_default_json(loads=lambda x: x)
psycopg2.extras.register_default_jsonb(loads=lambda x: x)

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE  = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]

# Relaxed CORS for local frontend dev
CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
