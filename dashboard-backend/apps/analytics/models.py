from django.db import models
from django.conf import settings

class Metric(models.Model):
    name       = models.CharField(max_length=100, db_index=True)
    value      = models.DecimalField(max_digits=18, decimal_places=4)
    unit       = models.CharField(max_length=30, blank=True)
    period     = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta       = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table        = "metrics"
        unique_together = [["name", "period"]]
        ordering        = ["-period"]
        indexes         = [models.Index(fields=["name", "period"])]
