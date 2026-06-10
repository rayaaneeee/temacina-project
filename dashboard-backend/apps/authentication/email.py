from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id: int, raw_token: str):
    """
    Celery task: sends the password reset email asynchronously.
    Retries up to 3 times on SMTP failure.
    """
    from apps.users.models import User
    try:
        user      = User.objects.get(id=user_id)
        reset_url = (
            f"{settings.FRONTEND_URL}/reset-password"
            f"?token={raw_token}"
        )
        # Plain-text body
        message = (
            f"Hello {user.first_name},\n\n"
            f"You requested a password reset for your Temacina account.\n\n"
            f"Click the link below to set a new password (valid for 1 hour):\n"
            f"{reset_url}\n\n"
            f"If you did not request this, please ignore this email.\n"
            f"Your password will remain unchanged.\n\n"
            f"— The Temacina Team"
        )
        send_mail(
            subject="Reset your Temacina password",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info("Password reset email sent to %s", user.email)
    except Exception as exc:
        logger.exception("Failed to send reset email to user %s", user_id)
        raise self.retry(exc=exc)
