import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.tests.factories import UserFactory
from apps.safex.tests.factories import (
    TradeShowFactory, SectorFactory, DocumentFactory,
    make_full_company, CompanyFactory, EmailFactory, PhoneFactory,
    CompanyEmail, CompanyPhone,
)

def get_items(resp):
    data = resp.json()["data"]
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    return data

@pytest.fixture
def auth_client():
    """Returns an APIClient authenticated with a fresh user JWT."""
    user   = UserFactory()
    client = APIClient()

    # Obtain JWT token through the login endpoint
    from django.test import Client as DjangoClient
    from django.urls import reverse as r

    django_client = DjangoClient()
    user.set_password("testpass123")
    user.save()

    resp   = django_client.post(
        r("auth-login"),
        {"email": user.email, "password": "testpass123"},
        content_type="application/json",
    )
    token = resp.json()["data"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client

@pytest.fixture
def admin_client():
    """Returns an APIClient authenticated as an Admin user."""
    user = UserFactory(role="admin")
    user.set_password("adminpass123")
    user.save()
    client = APIClient()

    from django.test import Client as DjangoClient
    from django.urls import reverse as r
    django_client = DjangoClient()
    resp  = django_client.post(
        r("auth-login"),
        {"email": user.email, "password": "adminpass123"},
        content_type="application/json",
    )
    token = resp.json()["data"]["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client

@pytest.mark.django_db
class TestTradeShowAPI:

    def test_list_trade_shows_authenticated(self, auth_client):
        TradeShowFactory.create_batch(3)
        resp = auth_client.get("/api/v1/trade-shows/")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert len(get_items(resp)) >= 3

    def test_list_trade_shows_requires_auth(self):
        client = APIClient()
        resp = client.get("/api/v1/trade-shows/")
        assert resp.status_code == 401

    def test_filter_trade_shows_by_year(self, auth_client):
        TradeShowFactory(exhibition_year=2024)
        TradeShowFactory(exhibition_year=2022)
        resp = auth_client.get("/api/v1/trade-shows/?exhibition_year=2024")
        assert resp.status_code == 200
        data = get_items(resp)
        assert all(ts["exhibition_year"] == 2024 for ts in data)

    def test_trade_show_detail(self, auth_client):
        ts   = TradeShowFactory()
        resp = auth_client.get(f"/api/v1/trade-shows/{ts.id}/")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == ts.id

    def test_trade_show_detail_not_found(self, auth_client):
        resp = auth_client.get("/api/v1/trade-shows/99999/")
        assert resp.status_code == 404

    def test_trade_show_stats(self, auth_client):
        ts = TradeShowFactory()
        make_full_company(trade_show=ts)
        resp = auth_client.get(f"/api/v1/trade-shows/{ts.id}/stats/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "document_count" in data
        assert "company_count"  in data

    def test_ingestion_progress(self, auth_client):
        ts = TradeShowFactory()
        DocumentFactory(trade_show=ts, ingestion_status="done")
        DocumentFactory(trade_show=ts, ingestion_status="pending")
        resp = auth_client.get(f"/api/v1/trade-shows/{ts.id}/ingestion-progress/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"]    == 2
        assert data["ingested"] == 1
        assert data["pct"]      == 50.0

@pytest.mark.django_db
class TestSectorAPI:

    def test_list_sectors(self, auth_client):
        SectorFactory.create_batch(4)
        resp = auth_client.get("/api/v1/sectors/")
        assert resp.status_code == 200
        assert len(get_items(resp)) >= 4

@pytest.mark.django_db
class TestCompanyListAPI:

    def test_list_companies(self, auth_client):
        make_full_company()
        resp = auth_client.get("/api/v1/companies/")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert len(get_items(resp)) >= 1

    def test_pagination_meta_present(self, auth_client):
        make_full_company()
        resp = auth_client.get("/api/v1/companies/")
        assert "meta" in resp.json() or (isinstance(resp.json().get("data"), dict) and "meta" in resp.json()["data"])

    def test_filter_by_trade_show_id(self, auth_client):
        ts = TradeShowFactory()
        c  = make_full_company(trade_show=ts)
        make_full_company(trade_show=TradeShowFactory())

        resp = auth_client.get(f"/api/v1/companies/?trade_show_id={ts.id}")
        assert resp.status_code == 200
        ids = [item["id"] for item in get_items(resp)]
        assert c.id in ids

    def test_filter_by_year(self, auth_client):
        ts = TradeShowFactory(exhibition_year=2024)
        c  = make_full_company(trade_show=ts)

        resp = auth_client.get("/api/v1/companies/?year=2024")
        ids  = [item["id"] for item in get_items(resp)]
        assert c.id in ids

    def test_filter_by_sector(self, auth_client):
        from apps.safex.models import CompanySector
        sector  = SectorFactory()
        company = CompanyFactory()
        CompanySector.objects.create(company=company, sector=sector)

        resp = auth_client.get(f"/api/v1/companies/?sector_id={sector.id}")
        assert resp.status_code == 200
        ids = [item["id"] for item in get_items(resp)]
        assert company.id in ids

    def test_search_by_name(self, auth_client):
        CompanyFactory(legal_name="SearchableCompany SARL")
        resp = auth_client.get("/api/v1/companies/?search=SearchableCompany")
        assert resp.status_code == 200
        names = [item["legal_name"] for item in get_items(resp)]
        assert any("SearchableCompany" in n for n in names)

    def test_filter_by_country(self, auth_client):
        from apps.safex.tests.factories import CompanyAddressFactory
        company = CompanyFactory()
        CompanyAddressFactory(company=company, country="Algeria")
        resp = auth_client.get("/api/v1/companies/?country=Algeria")
        ids  = [item["id"] for item in get_items(resp)]
        assert company.id in ids

    def test_combined_filters(self, auth_client):
        ts = TradeShowFactory(exhibition_year=2024)
        c  = make_full_company(trade_show=ts)
        resp = auth_client.get(
            f"/api/v1/companies/?trade_show_id={ts.id}&year=2024"
        )
        assert resp.status_code == 200

    def test_company_count_per_trade_show(self, auth_client):
        ts = TradeShowFactory()
        make_full_company(trade_show=ts)
        resp = auth_client.get("/api/v1/companies/count-per-trade-show/")
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)

@pytest.mark.django_db
class TestCompanyDetailAPI:

    def test_company_detail_full_fields(self, auth_client):
        company = make_full_company()
        resp = auth_client.get(f"/api/v1/companies/{company.id}/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        for field in ["id", "legal_name", "sectors", "addresses",
                      "phones", "emails", "websites", "contacts", "trade_shows"]:
            assert field in data, f"Missing field: {field}"

    def test_company_detail_not_found(self, auth_client):
        resp = auth_client.get("/api/v1/companies/99999999/")
        assert resp.status_code == 404

    def test_company_profile_cache_endpoint(self, auth_client):
        company = make_full_company()
        resp = auth_client.get(f"/api/v1/companies/{company.id}/profile/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"]         == company.id
        assert data["legal_name"] == company.legal_name

    def test_company_profile_cache_not_found(self, auth_client):
        resp = auth_client.get("/api/v1/companies/99999999/profile/")
        assert resp.status_code == 404

    def test_company_phones_endpoint(self, auth_client):
        company = CompanyFactory()
        phone   = PhoneFactory()
        CompanyPhone.objects.create(company=company, phone=phone)
        resp = auth_client.get(f"/api/v1/companies/{company.id}/phones/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "company_phones" in data
        assert "contact_phones" in data
        numbers = [p["full_phone_number"] for p in data["company_phones"]]
        assert phone.full_phone_number in numbers

    def test_company_emails_endpoint(self, auth_client):
        company = CompanyFactory()
        email   = EmailFactory()
        CompanyEmail.objects.create(company=company, email=email)
        resp = auth_client.get(f"/api/v1/companies/{company.id}/emails/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "company_emails" in data
        addresses = [e["email_address"] for e in data["company_emails"]]
        assert email.email_address in addresses

@pytest.mark.django_db
class TestDocumentAPI:

    def test_list_documents(self, auth_client):
        DocumentFactory.create_batch(3)
        resp = auth_client.get("/api/v1/documents/")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 3

    def test_filter_documents_by_trade_show(self, auth_client):
        ts  = TradeShowFactory()
        doc = DocumentFactory(trade_show=ts)
        DocumentFactory(trade_show=TradeShowFactory())
        resp = auth_client.get(f"/api/v1/documents/?trade_show_id={ts.id}")
        ids  = [d["id"] for d in get_items(resp)]
        assert doc.id in ids

    def test_filter_documents_by_status(self, auth_client):
        DocumentFactory(ingestion_status="done")
        DocumentFactory(ingestion_status="pending")
        resp = auth_client.get("/api/v1/documents/?status=done")
        assert resp.status_code == 200
        statuses = [d["ingestion_status"] for d in get_items(resp)]
        assert all(s == "done" for s in statuses)

    def test_document_detail(self, auth_client):
        doc  = DocumentFactory()
        resp = auth_client.get(f"/api/v1/documents/{doc.id}/")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == doc.id

@pytest.mark.django_db
class TestDashboardKPIAPI:

    def test_kpi_endpoint_returns_all_keys(self, auth_client):
        make_full_company()
        resp = auth_client.get("/api/v1/dashboard/kpis/")
        assert resp.status_code == 200
        data = resp.json()["data"]
        for key in ["total_companies", "total_trade_shows", "total_documents",
                    "total_emails", "total_phones", "companies_by_year",
                    "companies_by_country", "companies_by_sector"]:
            assert key in data

    def test_kpi_totals_are_integers(self, auth_client):
        make_full_company()
        data = auth_client.get("/api/v1/dashboard/kpis/").json()["data"]
        assert isinstance(data["total_companies"],   int)
        assert isinstance(data["total_trade_shows"], int)
        assert isinstance(data["total_documents"],   int)

@pytest.mark.django_db
class TestGlobalSearchAPI:

    def test_search_returns_all_result_buckets(self, auth_client):
        make_full_company()
        resp = auth_client.get("/api/v1/search/?q=company")
        assert resp.status_code == 200
        data = resp.json()["data"]
        for bucket in ["companies", "contacts", "emails", "phones"]:
            assert bucket in data

    def test_search_query_too_short_returns_400(self, auth_client):
        resp = auth_client.get("/api/v1/search/?q=x")
        assert resp.status_code == 400

    def test_search_empty_query_returns_400(self, auth_client):
        resp = auth_client.get("/api/v1/search/")
        assert resp.status_code == 400

    def test_search_finds_specific_company(self, auth_client):
        CompanyFactory(legal_name="UniqueTestCompany999")
        resp = auth_client.get("/api/v1/search/?q=UniqueTestCompany999")
        names = [c["legal_name"] for c in resp.json()["data"]["companies"]]
        assert "UniqueTestCompany999" in names

    def test_search_finds_email(self, auth_client):
        EmailFactory(email_address="unique999@test.dz")
        resp = auth_client.get("/api/v1/search/?q=unique999")
        addresses = [e["email_address"] for e in resp.json()["data"]["emails"]]
        assert "unique999@test.dz" in addresses

    def test_search_requires_auth(self):
        resp = APIClient().get("/api/v1/search/?q=test")
        assert resp.status_code == 401

@pytest.mark.django_db
class TestResponseEnvelope:
    """Verify the StandardJSONRenderer wraps every response correctly."""

    def test_success_response_has_correct_envelope(self, auth_client):
        TradeShowFactory()
        resp = auth_client.get("/api/v1/trade-shows/")
        body = resp.json()
        assert "success" in body
        assert "data"    in body
        assert "errors"  in body
        assert body["success"] is True
        assert body["errors"]  is None

    def test_error_response_has_correct_envelope(self, auth_client):
        resp = auth_client.get("/api/v1/trade-shows/99999/")
        body = resp.json()
        assert body["success"] is False
        assert body["data"]    is None
        assert body["errors"]  is not None

    def test_unauthenticated_response_envelope(self):
        resp = APIClient().get("/api/v1/trade-shows/")
        body = resp.json()
        assert body["success"] is False
