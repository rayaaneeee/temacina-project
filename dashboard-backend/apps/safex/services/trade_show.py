from django.db.models import Count
from django.core.cache import cache
from apps.safex.models import TradeShow, Document


class TradeShowService:

    @staticmethod
    def get_all_trade_shows():
        return TradeShow.objects.all().order_by("-exhibition_year", "name")

    @staticmethod
    def get_trade_show_stats(trade_show_id: int) -> dict:
        """KPI block for one trade show edition."""
        cache_key = f"trade_show:stats:{trade_show_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        ts = TradeShow.objects.get(id=trade_show_id)
        docs = Document.objects.filter(trade_show_id=trade_show_id)

        stats = {
            "id":            ts.id,
            "name":          ts.name,
            "year":          ts.exhibition_year,
            "city":          ts.city,
            "country":       ts.country,
            "document_count": docs.count(),
            "company_count":  (
                ts.companies.values("id").distinct().count()
                if hasattr(ts, "companies") else
                docs.aggregate(c=Count("companies__id", distinct=True))["c"] or 0
            ),
            "docs_by_type":  list(
                docs.values("document_type__label")
                    .annotate(count=Count("id"))
            ),
            "ingestion_status": list(
                docs.values("ingestion_status")
                    .annotate(count=Count("id"))
            ),
        }
        cache.set(cache_key, stats, timeout=300)
        return stats
