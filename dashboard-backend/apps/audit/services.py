from apps.audit.models import AuditLog


def write_log(
    user,
    action: str,
    entity_type: str,
    entity_id=None,
    details=None,
    ip_address=None,
):
    """
    Central helper called throughout the codebase to write audit entries.
    Always non-blocking — errors are silently logged, never raised.
    """
    import logging
    logger = logging.getLogger("audit")
    try:
        AuditLog.objects.create(
            user=user,
            action_type=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
    except Exception:
        logger.exception(
            "Audit write failed: action=%s entity=%s/%s",
            action, entity_type, entity_id
        )
