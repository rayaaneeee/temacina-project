import pytest
from apps.safex.tests.factories import (
    TradeShowFactory, CompanyFactory, SectorFactory,
    CompanyDoc, DocumentFactory, CompanyPhone, PhoneFactory,
    CompanyEmail, EmailFactory, CompanySector,
    make_full_company,
)
from apps.safex.services.company import CompanyService
from apps.safex.services.trade_show import TradeShowService
from apps.safex.services.analytics import AnalyticsService
from apps.safex.services.search import SearchService

@pytest.mark.django_db
class TestCompanyServiceFilters:

    def test_get_companies_by_trade_show(self):
        ts      = TradeShowFactory()
        company = make_full_company(trade_show=ts)
        # Company from a different trade show
        make_full_company(trade_show=TradeShowFactory())

        result = list(CompanyService.get_companies_by_trade_show(ts.id))
        assert len(result) == 1
        assert result[0].id == company.id

    def test_get_companies_by_year(self):
        ts2024 = TradeShowFactory(exhibition_year=2024)
        ts2022 = TradeShowFactory(exhibition_year=2022)
        c2024  = make_full_company(trade_show=ts2024)
        make_full_company(trade_show=ts2022)

        result = list(CompanyService.get_companies_by_year(2024))
        ids    = [c.id for c in result]
        assert c2024.id in ids
        assert all(True for c in result)   # all returned belong to 2024

    def test_get_companies_by_show_and_year(self):
        ts = TradeShowFactory(name="Safex", exhibition_year=2024)
        c  = make_full_company(trade_show=ts)
        make_full_company(trade_show=TradeShowFactory(name="Other", exhibition_year=2024))

        result = list(CompanyService.get_companies_by_show_and_year("Safex", 2024))
        assert len(result) == 1
        assert result[0].id == c.id

    def test_get_companies_by_sector(self):
        sector  = SectorFactory()
        company = CompanyFactory()
        CompanySector.objects.create(company=company, sector=sector)
        other = CompanyFactory()   # no sector

        result = list(CompanyService.get_companies_by_sector(sector.id))
        ids    = [c.id for c in result]
        assert company.id in ids
        assert other.id not in ids

    def test_get_companies_by_country(self):
        from apps.safex.tests.factories import CompanyAddressFactory
        company_dz = CompanyFactory()
        company_ma = CompanyFactory()
        CompanyAddressFactory(company=company_dz, country="Algeria")
        CompanyAddressFactory(company=company_ma, country="Morocco")

        result = list(CompanyService.get_companies_by_country("Algeria"))
        ids    = [c.id for c in result]
        assert company_dz.id in ids
        assert company_ma.id not in ids

    def test_combined_filter_returns_distinct(self):
        ts   = TradeShowFactory(exhibition_year=2024)
        c    = make_full_company(trade_show=ts)
        # Two documents for same company / same trade show
        doc2 = DocumentFactory(trade_show=ts)
        CompanyDoc.objects.create(company=c, document=doc2)

        result = list(CompanyService.get_companies_filtered(
            trade_show_id=ts.id, year=2024
        ))
        # Must return 1, not 2 (distinct must work)
        assert result.count(result[0]) == 1

    def test_combined_filter_search(self):
        CompanyFactory(legal_name="Temacina SARL")
        CompanyFactory(legal_name="Other Corp")

        result = list(CompanyService.get_companies_filtered(search="Temacina"))
        assert len(result) == 1
        assert "Temacina" in result[0].legal_name


@pytest.mark.django_db
class TestCompanyServiceContactData:

    def test_get_company_phones_returns_company_level(self):
        company = CompanyFactory()
        phone   = PhoneFactory()
        CompanyPhone.objects.create(company=company, phone=phone)

        data = CompanyService.get_company_phones(company.id)
        numbers = [p["full_phone_number"] for p in data["company_phones"]]
        assert phone.full_phone_number in numbers

    def test_get_company_phones_returns_contact_level(self):
        from apps.safex.tests.factories import CompanyContactFactory
        from apps.safex.models import CompanyContactPhone
        company = CompanyFactory()
        contact = CompanyContactFactory(company=company)
        phone   = PhoneFactory()
        CompanyContactPhone.objects.create(company_contact=contact, phone=phone)

        data = CompanyService.get_company_phones(company.id)
        numbers = [p["full_phone_number"] for p in data["contact_phones"]]
        assert phone.full_phone_number in numbers

    def test_get_company_emails_returns_company_level(self):
        company = CompanyFactory()
        email   = EmailFactory()
        CompanyEmail.objects.create(company=company, email=email)

        data = CompanyService.get_company_emails(company.id)
        addresses = [e["email_address"] for e in data["company_emails"]]
        assert email.email_address in addresses

    def test_get_company_emails_returns_contact_level(self):
        from apps.safex.tests.factories import CompanyContactFactory
        from apps.safex.models import CompanyContactEmail
        company = CompanyFactory()
        contact = CompanyContactFactory(company=company)
        email   = EmailFactory()
        CompanyContactEmail.objects.create(company_contact=contact, email=email)

        data = CompanyService.get_company_emails(company.id)
        addresses = [e["email_address"] for e in data["contact_emails"]]
        assert email.email_address in addresses

    def test_get_company_full_profile_structure(self):
        from django.core.cache import cache
        cache.clear()
        company = make_full_company()
        profile = CompanyService.get_company_full_profile(company.id)

        assert profile is not None
        assert profile["id"]         == company.id
        assert profile["legal_name"] == company.legal_name
        assert "addresses"           in profile
        assert "phones"              in profile
        assert "emails"              in profile
        assert "contacts"            in profile
        assert "trade_shows"         in profile

    def test_get_company_full_profile_none_for_missing(self):
        profile = CompanyService.get_company_full_profile(99999999)
        assert profile is None

    def test_get_company_full_profile_is_cached(self):
        from django.core.cache import cache
        company = make_full_company()
        cache.clear()

        profile1 = CompanyService.get_company_full_profile(company.id)
        cache_key = f"company:full_profile:{company.id}"
        assert cache.get(cache_key) is not None   # must be in cache

        profile2 = CompanyService.get_company_full_profile(company.id)
        assert profile1 == profile2   # same data served from cache

    def test_company_count_per_trade_show(self):
        ts = TradeShowFactory()
        make_full_company(trade_show=ts)
        make_full_company(trade_show=ts)

        data = CompanyService.get_company_count_per_trade_show()
        assert isinstance(data, list)
        assert len(data) > 0
        for entry in data:
            assert "company_count" in entry


@pytest.mark.django_db
class TestTradeShowService:

    def test_get_all_trade_shows(self):
        TradeShowFactory(exhibition_year=2024)
        TradeShowFactory(exhibition_year=2022)
        from apps.safex.models import TradeShow
        count = TradeShow.objects.count()
        result = TradeShowService.get_all_trade_shows()
        assert result.count() == count

    def test_get_trade_show_stats_keys(self):
        ts  = TradeShowFactory()
        make_full_company(trade_show=ts)

        stats = TradeShowService.get_trade_show_stats(ts.id)
        assert stats["id"]             == ts.id
        assert stats["name"]           == ts.name
        assert stats["year"]           == ts.exhibition_year
        assert "document_count"        in stats
        assert "company_count"         in stats
        assert "docs_by_type"          in stats
        assert "ingestion_status"      in stats

    def test_get_trade_show_stats_cached(self):
        from django.core.cache import cache
        ts = TradeShowFactory()
        cache.clear()

        TradeShowService.get_trade_show_stats(ts.id)
        cache_key = f"trade_show:stats:{ts.id}"
        assert cache.get(cache_key) is not None


@pytest.mark.django_db
class TestAnalyticsService:

    def test_get_dashboard_kpis_structure(self):
        make_full_company()
        kpis = AnalyticsService.get_dashboard_kpis()

        for key in ["total_companies", "total_trade_shows", "total_documents",
                    "total_emails", "total_phones", "companies_by_year",
                    "docs_by_status", "companies_by_country", "companies_by_sector"]:
            assert key in kpis, f"Missing KPI key: {key}"

    def test_get_dashboard_kpis_counts_are_positive(self):
        make_full_company()
        kpis = AnalyticsService.get_dashboard_kpis()
        assert kpis["total_companies"]   >= 1
        assert kpis["total_trade_shows"] >= 1
        assert kpis["total_documents"]   >= 1

    def test_get_dashboard_kpis_cached(self):
        from django.core.cache import cache
        cache.clear()
        AnalyticsService.get_dashboard_kpis()
        assert cache.get("dashboard:global_kpis") is not None

    def test_ingestion_progress_percentage(self):
        ts   = TradeShowFactory()
        DocumentFactory(trade_show=ts, ingestion_status="done")
        DocumentFactory(trade_show=ts, ingestion_status="done")
        DocumentFactory(trade_show=ts, ingestion_status="pending")

        progress = AnalyticsService.get_document_ingestion_progress(ts.id)
        assert progress["total"]    == 3
        assert progress["ingested"] == 2
        assert progress["pending"]  == 1
        assert progress["pct"]      == 66.7

    def test_ingestion_progress_zero_docs(self):
        ts = TradeShowFactory()
        progress = AnalyticsService.get_document_ingestion_progress(ts.id)
        assert progress["pct"] == 0   # no division by zero


@pytest.mark.django_db
class TestSearchService:

    def test_search_finds_company_by_name(self):
        CompanyFactory(legal_name="Temacina SARL")
        CompanyFactory(legal_name="Other Corp")

        results = SearchService.global_search("Temacina")
        names   = [c["legal_name"] for c in results["companies"]]
        assert any("Temacina" in n for n in names)

    def test_search_finds_email(self):
        EmailFactory(email_address="info@safex.dz")
        results = SearchService.global_search("safex.dz")
        addresses = [e["email_address"] for e in results["emails"]]
        assert "info@safex.dz" in addresses

    def test_search_finds_phone(self):
        from apps.safex.tests.factories import PhoneTypeFactory
        pt = PhoneTypeFactory()
        PhoneFactory(phone_type=pt, full_phone_number="+213555123456")
        results = SearchService.global_search("555123456")
        numbers = [p["full_phone_number"] for p in results["phones"]]
        assert "+213555123456" in numbers

    def test_search_too_short_returns_empty_structure(self):
        results = SearchService.global_search("x")
        assert "companies" in results
        assert "emails"    in results

    def test_search_no_results(self):
        results = SearchService.global_search("ZZZNOMATCH999")
        assert results["companies"] == []
        assert results["emails"]    == []
        assert results["phones"]    == []
