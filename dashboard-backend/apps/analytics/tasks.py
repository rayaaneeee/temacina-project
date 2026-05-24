from celery import shared_task
from .cache import invalidate_dashboard_cache
from apps.users.models import User

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_dashboard_metrics(self):
    """Invalidate all user dashboard caches — run every 5 minutes via Celery Beat."""
    for user in User.objects.filter(is_active=True).values_list("id", flat=True):
        invalidate_dashboard_cache(str(user))
