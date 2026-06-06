import pytest
from django.db import IntegrityError
from apps.safex.tests.factories import (
    TradeShowFactory, CompanyFactory, PhoneFactory,
    EmailFactory, DocumentFactory, SectorFactory,
    CompanySector, CompanyPhone, CompanyEmail, CompanyDoc,
)

@pytest.mark.django_db
class TestTradeShowModel:

    def test_create_trade_show(self):
        ts = TradeShowFactory(name="Safex", exhibition_year=2024)
        assert ts.id is not None
        assert str(ts) == "Safex (2024)"

    def test_unique_together_name_year(self):
        TradeShowFactory(name="Safex", exhibition_year=2024)
        with pytest.raises(IntegrityError):
            TradeShowFactory(name="Safex", exhibition_year=2024)

    def test_ordering_by_year_desc(self):
        from apps.safex.models import TradeShow
        TradeShowFactory(name="A", exhibition_year=2022)
        TradeShowFactory(name="B", exhibition_year=2025)
        shows = list(TradeShow.objects.all())
        assert shows[0].exhibition_year >= shows[-1].exhibition_year

@pytest.mark.django_db
class TestCompanyModel:

    def test_create_company(self):
        c = CompanyFactory()
        assert c.id is not None
        assert c.legal_name != ""

    def test_legal_name_unique(self):
        CompanyFactory(legal_name="Temacina SARL")
        with pytest.raises(IntegrityError):
            CompanyFactory(legal_name="Temacina SARL")

    def test_company_sector_relationship(self):
        company = CompanyFactory()
        sector  = SectorFactory()
        CompanySector.objects.create(company=company, sector=sector)
        assert company.sectors.count() == 1
        assert company.sectors.first().title == sector.title

    def test_company_phone_relationship(self):
        company = CompanyFactory()
        phone   = PhoneFactory()
        CompanyPhone.objects.create(company=company, phone=phone)
        assert company.phones.count() == 1
        assert company.phones.first().full_phone_number == phone.full_phone_number

    def test_company_email_relationship(self):
        company = CompanyFactory()
        email   = EmailFactory()
        CompanyEmail.objects.create(company=company, email=email)
        assert company.emails.count() == 1
        assert company.emails.first().email_address == email.email_address

    def test_company_document_relationship(self):
        company = CompanyFactory()
        doc     = DocumentFactory()
        CompanyDoc.objects.create(company=company, document=doc)
        assert company.documents.count() == 1

@pytest.mark.django_db
class TestEmailModel:

    def test_email_unique(self):
        EmailFactory(email_address="test@test.dz")
        with pytest.raises(IntegrityError):
            EmailFactory(email_address="test@test.dz")

    def test_is_professional_flag(self):
        pro    = EmailFactory(is_professional=True)
        nonpro = EmailFactory(is_professional=False)
        assert pro.is_professional is True
        assert nonpro.is_professional is False

@pytest.mark.django_db
class TestPhoneModel:

    def test_create_phone_with_type(self):
        phone = PhoneFactory()
        assert phone.phone_type is not None
        assert phone.full_phone_number.startswith("+213")

    def test_unique_phone_per_type(self):
        from apps.safex.tests.factories import PhoneTypeFactory
        pt = PhoneTypeFactory()
        PhoneFactory(phone_type=pt, full_phone_number="+2130551234567")
        with pytest.raises(IntegrityError):
            PhoneFactory(phone_type=pt, full_phone_number="+2130551234567")
