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
