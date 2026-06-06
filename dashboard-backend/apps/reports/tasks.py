from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def generate_report(self, report_id: str):
    from .models import Report

    try:
        report = Report.objects.get(id=report_id)
        report.status = Report.Status.PROCESSING
        report.save(update_fields=["status"])

        # ── Replace with real generation logic ──
        # e.g. use reportlab for PDF, openpyxl for Excel
        logger.info("Generating report %s", report_id)

        report.status = Report.Status.READY
        report.save(update_fields=["status", "updated_at"])
    except Exception as exc:
        report.status    = Report.Status.FAILED
        report.error_msg = str(exc)
        report.save(update_fields=["status", "error_msg"])
        raise self.retry(exc=exc)
