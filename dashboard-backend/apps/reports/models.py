from django.db import models
from django.conf import settings
import uuid

class Report(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        PROCESSING = "processing", "Processing"
        READY      = "ready",      "Ready"
        FAILED     = "failed",     "Failed"

    class Format(models.TextChoices):
        PDF   = "pdf",   "PDF"
        EXCEL = "excel", "Excel"
        CSV   = "csv",   "CSV"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name="reports")
    title      = models.CharField(max_length=255)
    status     = models.CharField(max_length=20, choices=Status.choices,
                                  default=Status.PENDING, db_index=True)
    format     = models.CharField(max_length=10, choices=Format.choices, default=Format.PDF)
    file       = models.FileField(upload_to="reports/%Y/%m/", null=True, blank=True)
    error_msg  = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reports"
        ordering = ["-created_at"]
