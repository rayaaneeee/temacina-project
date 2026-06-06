import factory
from factory.django import DjangoModelFactory
from faker import Faker
from apps.safex.models import (
    TradeShow, Sector, DocumentType, PhoneType, SocialNetworkType,
    Language, Company, CompanyContact, CompanyAddress,
    Phone, Email, Website, SocialNetworkAccount,
    Document, CompanyDoc, CompanyPhone, CompanyEmail,
    CompanyWebsite, CompanySector,
)

fake = Faker()

class TradeShowFactory(DjangoModelFactory):
    class Meta:
        model = TradeShow

    name            = factory.Sequence(lambda n: f"Safex {n}")
    exhibition_year = factory.Iterator([2022, 2023, 2024, 2025])
    venue_name      = factory.LazyAttribute(lambda _: fake.company())
    city            = factory.LazyAttribute(lambda _: fake.city())
    country         = "Algeria"

class SectorFactory(DjangoModelFactory):
    class Meta:
        model = Sector

    title = factory.Sequence(lambda n: f"Sector_{n}")

class DocumentTypeFactory(DjangoModelFactory):
    class Meta:
        model = DocumentType

    code  = factory.Sequence(lambda n: f"TYPE_{n}")
    label = factory.Sequence(lambda n: f"Type Label {n}")

class PhoneTypeFactory(DjangoModelFactory):
    class Meta:
        model = PhoneType

    code  = factory.Sequence(lambda n: f"PHONE_TYPE_{n}")
    label = factory.Sequence(lambda n: f"Phone Type {n}")

class SocialNetworkTypeFactory(DjangoModelFactory):
    class Meta:
        model = SocialNetworkType

    code  = factory.Iterator(["LINKEDIN", "FACEBOOK", "INSTAGRAM", "X", "TIKTOK"])
    label = factory.LazyAttribute(lambda o: o.code.capitalize())

class LanguageFactory(DjangoModelFactory):
    class Meta:
        model = Language

    language = factory.Iterator(["Arabic", "French", "English"])

class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = Company

    legal_name            = factory.Sequence(lambda n: f"Company {n} SARL")
    normalized_legal_name = factory.LazyAttribute(
        lambda o: o.legal_name.lower().replace(" ", "_")
    )
    logo     = None
    metadata = None

class CompanyContactFactory(DjangoModelFactory):
    class Meta:
        model = CompanyContact

    company    = factory.SubFactory(CompanyFactory)
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name  = factory.LazyAttribute(lambda _: fake.last_name())
    role       = factory.Iterator(["CEO", "Manager", "Sales", "Engineer"])

class CompanyAddressFactory(DjangoModelFactory):
    class Meta:
        model = CompanyAddress

    company     = factory.SubFactory(CompanyFactory)
    street      = factory.LazyAttribute(lambda _: fake.street_address())
    postal_code = factory.LazyAttribute(lambda _: fake.postcode())
    city        = factory.LazyAttribute(lambda _: fake.city())
    country     = "Algeria"

class PhoneFactory(DjangoModelFactory):
    class Meta:
        model = Phone

    phone_type        = factory.SubFactory(PhoneTypeFactory)
    country_dial_code = "+213"
    phone_number      = factory.Sequence(lambda n: f"055{n:07d}")
    full_phone_number = factory.LazyAttribute(
        lambda o: f"{o.country_dial_code}{o.phone_number}"
    )
    normalized_phone_number = factory.LazyAttribute(lambda o: o.full_phone_number)

class EmailFactory(DjangoModelFactory):
    class Meta:
        model = Email

    email_address            = factory.Sequence(lambda n: f"contact{n}@company{n}.dz")
    normalized_email_address = factory.LazyAttribute(lambda o: o.email_address.lower())
    is_professional          = True

class WebsiteFactory(DjangoModelFactory):
    class Meta:
        model = Website

    url            = factory.Sequence(lambda n: f"https://company{n}.dz")
    normalized_url = factory.LazyAttribute(lambda o: o.url)
    website_type   = "official"

class SocialNetworkAccountFactory(DjangoModelFactory):
    class Meta:
        model = SocialNetworkAccount

    social_network_type   = factory.SubFactory(SocialNetworkTypeFactory)
    account_value         = factory.Sequence(lambda n: f"@company_{n}")
    normalized_account_value = factory.LazyAttribute(lambda o: o.account_value.lower())
    profile_url           = factory.Sequence(lambda n: f"https://linkedin.com/company/company_{n}")

class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    trade_show       = factory.SubFactory(TradeShowFactory)
    document_type    = factory.SubFactory(DocumentTypeFactory)
    file_name        = factory.Sequence(lambda n: f"catalogue_{n}.pdf")
    file_hash        = factory.Sequence(lambda n: f"abc{n:061d}")
    page_count       = factory.LazyAttribute(lambda _: fake.random_int(1, 200))
    ingestion_status = "done"

def make_full_company(trade_show=None):
    ts       = trade_show or TradeShowFactory()
    doc_type = DocumentTypeFactory()
    doc      = DocumentFactory(trade_show=ts, document_type=doc_type)
    company  = CompanyFactory()
    sector   = SectorFactory()

    CompanyAddressFactory(company=company)
    CompanySector.objects.create(company=company, sector=sector)
    CompanyDoc.objects.create(company=company, document=doc)

    phone = PhoneFactory()
    CompanyPhone.objects.create(company=company, phone=phone)

    email = EmailFactory()
    CompanyEmail.objects.create(company=company, email=email)

    website = WebsiteFactory()
    CompanyWebsite.objects.create(company=company, website=website)

    CompanyContactFactory(company=company)

    return company
