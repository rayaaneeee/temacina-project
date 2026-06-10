from django.db import models


class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        LOGIN           = "LOGIN",           "Login"
        LOGOUT          = "LOGOUT",          "Logout"
        LOGIN_FAILED    = "LOGIN_FAILED",    "Login Failed"
        PASSWORD_RESET  = "PASSWORD_RESET",  "Password Reset"
        USER_CREATED    = "USER_CREATED",    "User Created"
        USER_UPDATED    = "USER_UPDATED",    "User Updated"
        USER_DELETED    = "USER_DELETED",    "User Deleted"
        ROLE_CHANGED    = "ROLE_CHANGED",    "Role Changed"
        COMPANY_VIEWED  = "COMPANY_VIEWED",  "Company Viewed"
        DATA_EXPORTED   = "DATA_EXPORTED",   "Data Exported"
        ACCESS_DENIED   = "ACCESS_DENIED",   "Access Denied"

    user        = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL,
        null=True, related_name="audit_logs"
    )
    action_type = models.CharField(max_length=50, choices=ActionType.choices,
                                   db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id   = models.IntegerField(null=True, blank=True)
    details     = models.JSONField(null=True, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        managed  = False
        db_table = "audit_logs"
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["action_type", "created_at"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        return f"{self.action_type} | {self.user} | {self.created_at}"
