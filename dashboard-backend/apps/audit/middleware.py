import uuid
from .models import AuditLog

SKIP_PATHS = {"/api/health/", "/static/", "/media/"}

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(p) for p in SKIP_PATHS):
            return self.get_response(request)

        request.request_id = str(uuid.uuid4())
        response = self.get_response(request)

        user = request.user if request.user.is_authenticated else None
        AuditLog.objects.create(
            user       = user,
            action     = request.method,
            resource   = request.path,
            ip_address = self._get_ip(request),
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:500],
            request_id = request.request_id,
            status     = response.status_code,
        )
        return response

    @staticmethod
    def _get_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
