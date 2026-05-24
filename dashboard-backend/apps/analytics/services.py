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
