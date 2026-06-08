from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.services import AuthService
from apps.authentication.throttles import LoginRateThrottle, PasswordResetThrottle
from apps.authentication.api.serializers import (
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [LoginRateThrottle]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        ip         = _get_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        try:
            tokens = AuthService.login(
                email=s.validated_data["email"],
                password=s.validated_data["password"],
                ip=ip,
                user_agent=user_agent,
            )
        except PermissionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(tokens)


class LogoutView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "Refresh token required."},
                            status=status.HTTP_400_BAD_REQUEST)
        AuthService.logout(refresh, request.user, _get_ip(request))
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [PasswordResetThrottle]

    def post(self, request):
        s = PasswordResetRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        AuthService.request_password_reset(
            email=s.validated_data["email"],
            ip=_get_ip(request),
        )
        # Always return 200 — never reveal whether email exists
        return Response({
            "detail": "If this email is registered, a reset link has been sent."
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = PasswordResetConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            AuthService.reset_password(
                raw_token=s.validated_data["token"],
                new_password=s.validated_data["new_password"],
                ip=_get_ip(request),
            )
        except ValueError as e:
            return Response({"detail": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Password reset successful. Please log in."})


class ChangePasswordView(APIView):
    def post(self, request):
        from apps.users.api.serializers import ChangePasswordSerializer
        s = ChangePasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(s.validated_data["old_password"]):
            return Response({"detail": "Current password is incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(s.validated_data["new_password"])
        user.save(update_fields=["password"])
        # Invalidate all sessions except current
        from apps.audit.services import write_log
        write_log(user=user, action="PASSWORD_RESET",
                  entity_type="User", entity_id=user.id,
                  details={"step": "self_change"}, ip_address=_get_ip(request))
        return Response({"detail": "Password changed successfully."})


def _get_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "Old password incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated."})
