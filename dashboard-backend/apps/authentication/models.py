import uuid
import secrets
from datetime import timedelta
from django.db import models
from django.utils import timezone


class PasswordResetToken(models.Model):
    """
    Secure one-time password reset token.
    - Token is a 64-char cryptographically random hex string.
    - Expires after 1 hour.
    - Invalidated immediately on use.
    - Never stored in plain text — token_hash (SHA-256) is stored.
    """
    user       = models.ForeignKey(
        "users.User", on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at    = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        # managed=True — Django creates this table
        db_table = "password_reset_tokens"
        indexes  = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["user", "expires_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return (
            self.used_at   is None
            and self.expires_at > timezone.now()
        )

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    @classmethod
    def generate(cls, user, ip_address=None):
        """
        Generates a new token, invalidates all previous tokens for this user,
        stores only the SHA-256 hash, and returns the raw token string.
        """
        import hashlib
        # Invalidate all previous tokens for this user
        cls.objects.filter(user=user, used_at=None).update(
            used_at=timezone.now()
        )
        raw_token = secrets.token_hex(32)  # 64-char hex, 256 bits of entropy
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        cls.objects.create(
            user=user,
            token_hash=token_hash,
            ip_address=ip_address,
        )
        return raw_token  # only returned once, never stored
