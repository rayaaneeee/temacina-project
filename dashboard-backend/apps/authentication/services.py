import hashlib
import logging
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User, UserSession
from apps.authentication.models import PasswordResetToken
from apps.authentication.throttles import AccountLockoutMixin
from apps.audit.services import write_log

logger = logging.getLogger(__name__)


class AuthService:

    # ── LOGIN ─────────────────────────────────────────────────────
    @staticmethod
    def login(email: str, password: str, ip: str, user_agent: str) -> dict:
        """
        Full login flow:
        1. Check account lockout
        2. Authenticate credentials
        3. On failure → record attempt, maybe lock account, log
        4. On success → clear lockout, open session, issue JWT, log
        """
        if AccountLockoutMixin.is_locked(email):
            raise PermissionError(
                "Account temporarily locked due to too many failed attempts. "
                "Try again in 15 minutes."
            )

        user = authenticate(username=email, password=password)

        if not user:
            AccountLockoutMixin.record_failure(email)
            # Log even for unknown emails (do not leak user existence)
            write_log(
                user=None,
                action="LOGIN_FAILED",
                entity_type="User",
                entity_id=None,
                details={"email_attempted": email},
                ip_address=ip,
            )
            raise ValueError("Invalid email or password.")

        if not user.is_active:
            raise PermissionError("Account is deactivated. Contact an admin.")

        # Success path
        AccountLockoutMixin.clear(email)

        session = UserSession.objects.create(
            user=user,
            ip_address=ip,
            user_agent=user_agent[:500] if user_agent else "",
            is_active=True,
        )
        refresh = RefreshToken.for_user(user)
        # Embed session id in token for traceability
        refresh["session_id"] = session.id
        refresh["role"]       = user.role_name

        write_log(
            user=user, action="LOGIN",
            entity_type="UserSession",
            entity_id=session.id,
            details={"ip": ip},
            ip_address=ip,
        )
        return {
            "access":     str(refresh.access_token),
            "refresh":    str(refresh),
            "session_id": session.id,
            "user": {
                "id":        user.id,
                "full_name": user.full_name,
                "email":     user.email,
                "role":      user.role_name,
                "sector":    user.sector.name if user.sector else None,
            },
        }

    # ── LOGOUT ────────────────────────────────────────────────────
    @staticmethod
    def logout(refresh_token_str: str, user, ip: str):
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        try:
            token      = RefreshToken(refresh_token_str)
            session_id = token.get("session_id")
            token.blacklist()
            if session_id:
                UserSession.objects.filter(id=session_id).update(
                    logout_at=timezone.now(),
                    is_active=False,
                )
            write_log(
                user=user, action="LOGOUT",
                entity_type="UserSession",
                entity_id=session_id,
                details=None, ip_address=ip,
            )
        except TokenError:
            pass  # already blacklisted; ignore

    # ── FORGOT PASSWORD ───────────────────────────────────────────
    @staticmethod
    def request_password_reset(email: str, ip: str) -> bool:
        """
        Always returns True regardless of whether email exists
        to prevent user enumeration attacks.
        Token generation and email dispatch are done asynchronously.
        """
        from apps.authentication.email import send_password_reset_email
        try:
            user = User.objects.get(email=email, is_active=True)
            raw_token = PasswordResetToken.generate(user=user, ip_address=ip)
            send_password_reset_email.delay(
                user_id=user.id,
                raw_token=raw_token,
            )
            write_log(
                user=user, action="PASSWORD_RESET",
                entity_type="PasswordResetToken",
                entity_id=None,
                details={"step": "requested", "ip": ip},
                ip_address=ip,
            )
        except User.DoesNotExist:
            # Deliberately do nothing — same response either way
            logger.info("Password reset requested for unknown email: %s", email)
        return True

    # ── RESET PASSWORD ─────────────────────────────────────────────
    @staticmethod
    def reset_password(raw_token: str, new_password: str, ip: str) -> bool:
        import hashlib
        from django.contrib.auth.password_validation import validate_password

        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        try:
            token_obj = PasswordResetToken.objects.select_related("user").get(
                token_hash=token_hash
            )
        except PasswordResetToken.DoesNotExist:
            raise ValueError("Invalid or expired reset link.")

        if not token_obj.is_valid:
            raise ValueError("Reset link has expired or already been used.")

        validate_password(new_password, token_obj.user)  # runs validators
        token_obj.user.set_password(new_password)
        token_obj.user.save(update_fields=["password"])
        token_obj.mark_used()

        # Invalidate ALL existing sessions for this user (force re-login)
        UserSession.objects.filter(
            user=token_obj.user, is_active=True
        ).update(logout_at=timezone.now(), is_active=False)

        write_log(
            user=token_obj.user, action="PASSWORD_RESET",
            entity_type="User",
            entity_id=token_obj.user.id,
            details={"step": "completed", "ip": ip},
            ip_address=ip,
        )
        return True

    @staticmethod
    def logout(refresh_token: str) -> bool:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception:
            return False
