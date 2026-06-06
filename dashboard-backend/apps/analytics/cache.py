from django.core.cache import cache

DASHBOARD_METRICS_TTL = 300   # 5 min

def get_dashboard_cache_key(user_id: str) -> str:
    return f"dashboard:metrics:{user_id}"

def invalidate_dashboard_cache(user_id: str):
    cache.delete(get_dashboard_cache_key(user_id))
