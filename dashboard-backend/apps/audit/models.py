from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                   on_delete=models.SET_NULL, related_name="audit_logs")
    action     = models.CharField(max_length=50)
    resource   = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=36, blank=True)
    status     = models.PositiveSmallIntegerField()
    timestamp  = models.DateTimeField(auto_now_add=True, db_index=True)
    extra      = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes  = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
        ]
