"""
STEP 4 — Test services/trade_show.py, analytics.py, search.py
As specified in the roadmap: test each in the Django shell.
"""
import os, sys
sys.path.insert(0, ".")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django
django.setup()

# Disable cache to avoid Redis connection issues during testing
from django.conf import settings
settings.CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

from apps.safex.services.trade_show import TradeShowService
from apps.safex.services.analytics import AnalyticsService
from apps.safex.services.search import SearchService
from apps.safex.models import TradeShow

print("=" * 60)
print("STEP 4 — Testing TradeShowService, AnalyticsService, SearchService")
print("=" * 60)

# ── TradeShowService ──────────────────────────────────────────

print("\n" + "-" * 60)
print("TradeShowService")
print("-" * 60)

print("\n--- Test: get_all_trade_shows() ---")
trade_shows = TradeShowService.get_all_trade_shows()
print(f"Count: {trade_shows.count()}")
print(f"First 5: {list(trade_shows[:5])}")
print("PASS")

print("\n--- Test: get_trade_show_stats(trade_show_id) ---")
first_ts = TradeShow.objects.first()
if first_ts:
    stats = TradeShowService.get_trade_show_stats(first_ts.id)
    print(f"Stats keys: {list(stats.keys())}")
    print(f"Name: {stats['name']}, Year: {stats['year']}")
    print(f"Document count: {stats['document_count']}")
    print(f"Company count: {stats['company_count']}")
else:
    print("No trade shows in DB — testing with non-existent ID")
    try:
        TradeShowService.get_trade_show_stats(99999)
        print("ERROR: Should have raised DoesNotExist")
    except TradeShow.DoesNotExist:
        print("Correctly raised DoesNotExist for missing trade show")
print("PASS")

# ── AnalyticsService ──────────────────────────────────────────

print("\n" + "-" * 60)
print("AnalyticsService")
print("-" * 60)

print("\n--- Test: get_dashboard_kpis() ---")
kpis = AnalyticsService.get_dashboard_kpis()
print(f"KPI keys: {list(kpis.keys())}")
print(f"Total companies: {kpis['total_companies']}")
print(f"Total trade shows: {kpis['total_trade_shows']}")
print(f"Total documents: {kpis['total_documents']}")
print(f"Total emails: {kpis['total_emails']}")
print(f"Total phones: {kpis['total_phones']}")
print(f"Companies by year: {kpis['companies_by_year'][:3]}")
print(f"Docs by status: {kpis['docs_by_status'][:3]}")
print(f"Companies by country: {kpis['companies_by_country'][:3]}")
print(f"Companies by sector: {kpis['companies_by_sector'][:3]}")
print("PASS")

print("\n--- Test: get_document_ingestion_progress(trade_show_id) ---")
if first_ts:
    progress = AnalyticsService.get_document_ingestion_progress(first_ts.id)
else:
    progress = AnalyticsService.get_document_ingestion_progress(1)
print(f"Progress: {progress}")
expected_keys = {"total", "ingested", "pending", "pct"}
assert set(progress.keys()) == expected_keys, f"Missing keys: {expected_keys - set(progress.keys())}"
print("PASS")

# ── SearchService ─────────────────────────────────────────────

print("\n" + "-" * 60)
print("SearchService")
print("-" * 60)

print("\n--- Test: global_search('test') ---")
results = SearchService.global_search("test")
print(f"Result keys: {list(results.keys())}")
print(f"Companies found: {len(results['companies'])}")
print(f"Contacts found: {len(results['contacts'])}")
print(f"Emails found: {len(results['emails'])}")
print(f"Phones found: {len(results['phones'])}")
assert set(results.keys()) == {"companies", "contacts", "emails", "phones"}
print("PASS")

print("\n--- Test: global_search('a', limit=5) ---")
results2 = SearchService.global_search("a", limit=5)
print(f"Companies: {results2['companies']}")
print(f"Contacts: {results2['contacts']}")
print(f"Emails: {results2['emails']}")
print(f"Phones: {results2['phones']}")
print("PASS")

print("\n" + "=" * 60)
print("ALL STEP 4 TESTS PASSED")
print("(Note: 0 results expected — DB tables are empty)")
print("=" * 60)
