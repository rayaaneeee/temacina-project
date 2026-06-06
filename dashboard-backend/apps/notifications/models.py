from django.db import models
from django.conf import settings
import uuid

class Notification(models.Model):
    class Type(models.TextChoices):
        INFO    = "info",    "Info"
        WARNING = "warning", "Warning"
        ERROR   = "error",   "Error"
        SUCCESS = "success", "Success"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="notifications")
    title      = models.CharField(max_length=255)
    message    = models.TextField()
    type       = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    is_read    = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
