# Django admin configuration for audit logs
from django.contrib import admin
from apps.audit.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "action_type", "user", "entity_type", "created_at"]
    list_filter = ["action_type", "created_at", "entity_type"]
    search_fields = ["user__email", "entity_type"]
    readonly_fields = ["created_at"]
