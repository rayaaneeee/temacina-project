from django.db.models import Count, Q
from django.core.cache import cache
from apps.safex.models import Company, Document, TradeShow, Email, Phone


class AnalyticsService:

    @staticmethod
    def get_dashboard_kpis() -> dict:
        cache_key = "dashboard:global_kpis"
        cached = cache.get(cache_key)
        if cached:
            return cached

        data = {
            "total_companies":   Company.objects.count(),
            "total_trade_shows": TradeShow.objects.count(),
            "total_documents":   Document.objects.count(),
            "total_emails":      Email.objects.count(),
            "total_phones":      Phone.objects.count(),
            "companies_by_year": list(
                Company.objects
                .values("documents__trade_show__exhibition_year")
                .annotate(count=Count("id", distinct=True))
                .order_by("documents__trade_show__exhibition_year")
            ),
            "docs_by_status": list(
                Document.objects
                .values("ingestion_status")
                .annotate(count=Count("id"))
            ),
            "companies_by_country": list(
                Company.objects
                .values("addresses__country")
                .annotate(count=Count("id", distinct=True))
                .order_by("-count")[:10]
            ),
            "companies_by_sector": list(
                Company.objects
                .values("sectors__title")
                .annotate(count=Count("id", distinct=True))
                .order_by("-count")
            ),
        }
        cache.set(cache_key, data, timeout=300)
        return data

    @staticmethod
    def get_document_ingestion_progress(trade_show_id: int) -> dict:
        docs = Document.objects.filter(trade_show_id=trade_show_id)
        total = docs.count()
        ingested = docs.filter(ingestion_status="done").count()
        return {
            "total":    total,
            "ingested": ingested,
            "pending":  total - ingested,
            "pct":      round(ingested / total * 100, 1) if total else 0,
        }
