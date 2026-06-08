from rest_framework.throttling import AnonRateThrottle
from django.core.cache import cache
from rest_framework.exceptions import Throttled
import hashlib


class LoginRateThrottle(AnonRateThrottle):
    """5 attempts per minute per IP."""
    scope = "login"
    rate  = "5/min"


class PasswordResetThrottle(AnonRateThrottle):
    """3 reset requests per hour per IP."""
    scope = "password_reset"
    rate  = "3/hour"


class AccountLockoutMixin:
    """
    Locks an account for 15 minutes after 5 consecutive failed logins.
    Key stored in Redis with TTL.
    """
    MAX_ATTEMPTS = 5
    LOCKOUT_SEC  = 900   # 15 minutes

    @staticmethod
    def _key(email: str) -> str:
        h = hashlib.md5(email.lower().encode()).hexdigest()
        return f"login_attempts:{h}"

    @classmethod
    def is_locked(cls, email: str) -> bool:
        val = cache.get(cls._key(email))
        return val is not None and int(val) >= cls.MAX_ATTEMPTS

    @classmethod
    def record_failure(cls, email: str):
        key  = cls._key(email)
        curr = cache.get(key, 0)
        cache.set(key, int(curr) + 1, timeout=cls.LOCKOUT_SEC)

    @classmethod
    def clear(cls, email: str):
        cache.delete(cls._key(email))
