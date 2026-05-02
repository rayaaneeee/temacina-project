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
