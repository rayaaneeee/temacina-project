from django.db import models


# ════════════════════════════════════════════════════════════
# LOOKUP / REFERENCE TABLES
# ════════════════════════════════════════════════════════════

class TradeShow(models.Model):
    """
    One edition of a trade show, uniquely identified by (name, exhibition_year).
    exhibition_year must be between 2022 and 2030.
    """
    name            = models.CharField(max_length=255)
    exhibition_year = models.IntegerField()
    venue_name      = models.CharField(max_length=255, null=True, blank=True)
    city            = models.CharField(max_length=255, null=True, blank=True)
    country         = models.CharField(max_length=255, null=True, blank=True)
    metadata        = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "trade_shows"
        unique_together = [("name", "exhibition_year")]
        ordering = ["-exhibition_year", "name"]
        indexes  = [models.Index(fields=["exhibition_year"])]

    def __str__(self):
        return f"{self.name} ({self.exhibition_year})"


class Sector(models.Model):
    """
    Allowed values: Industry, Agriculture, Construction, ITech, Others.
    """
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        managed  = False
        db_table = "sectors"
        ordering = ["title"]

    def __str__(self):
        return self.title


class DocumentType(models.Model):
    """
    Allowed codes: CARTE_VISITE, CATALOGUE, ANNUAIRE, FLYER, MAGAZINE.
    """
    code  = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=255, unique=True)

    class Meta:
        managed  = False
        db_table = "document_types"

    def __str__(self):
        return self.label


class PhoneType(models.Model):
    """
    Allowed codes: FIX, FAX, MOBILE, WHATSAPP, WECHAT, TELEGRAM.
    """
    code  = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=255, unique=True)

    class Meta:
        managed  = False
        db_table = "phone_types"

    def __str__(self):
        return self.label


class SocialNetworkType(models.Model):
    """
    Allowed codes: X, TIKTOK, INSTAGRAM, FACEBOOK, YOUTUBE, LINKEDIN.
    """
    code  = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=255, unique=True)

    class Meta:
        managed  = False
        db_table = "social_network_types"

    def __str__(self):
        return self.label


class Language(models.Model):
    language = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "languages"

    def __str__(self):
        return self.language or str(self.id)


# ════════════════════════════════════════════════════════════
# CORE BUSINESS ENTITIES
# ════════════════════════════════════════════════════════════

class Company(models.Model):
    """
    Source-of-truth business entity.
    A company can appear in multiple trade shows (via company_docs → documents → trade_shows).
    """
    legal_name            = models.CharField(max_length=255, unique=True)
    normalized_legal_name = models.CharField(max_length=255, null=True, blank=True)
    logo                  = models.CharField(max_length=500, null=True, blank=True)
    metadata              = models.JSONField(null=True, blank=True)

    # Many-to-many relationships (declared here for ORM convenience)
    sectors      = models.ManyToManyField(Sector,      through="CompanySector",
                                          related_name="companies")
    phones       = models.ManyToManyField("Phone",     through="CompanyPhone",
                                          related_name="companies")
    emails       = models.ManyToManyField("Email",     through="CompanyEmail",
                                          related_name="companies")
    websites     = models.ManyToManyField("Website",   through="CompanyWebsite",
                                          related_name="companies")
    documents    = models.ManyToManyField("Document",  through="CompanyDoc",
                                          related_name="companies")
    social_networks = models.ManyToManyField(
        "SocialNetworkAccount",
        through="CompanySocialNetwork",
        related_name="companies",
    )

    class Meta:
        managed  = False
        db_table = "companies"
        ordering = ["legal_name"]
        indexes  = [
            models.Index(fields=["legal_name"]),
            models.Index(fields=["normalized_legal_name"]),
        ]

    def __str__(self):
        return self.legal_name


class CompanyContact(models.Model):
    company    = models.ForeignKey(Company, on_delete=models.CASCADE,
                                   related_name="contacts")
    first_name = models.CharField(max_length=255)
    last_name  = models.CharField(max_length=255, null=True, blank=True)
    role       = models.CharField(max_length=255, null=True, blank=True)
    metadata   = models.JSONField(null=True, blank=True)

    phones  = models.ManyToManyField("Phone",  through="CompanyContactPhone",
                                      related_name="contact_owners")
    emails  = models.ManyToManyField("Email",  through="CompanyContactEmail",
                                      related_name="contact_owners")
    social_networks = models.ManyToManyField(
        "SocialNetworkAccount",
        through="CompanyContactSocialNetwork",
        related_name="contact_owners",
    )

    class Meta:
        managed  = False
        db_table = "company_contacts"
        unique_together = [("company", "first_name", "last_name", "role")]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["last_name"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''} @ {self.company}"


class CompanyAddress(models.Model):
    company     = models.ForeignKey(Company, on_delete=models.CASCADE,
                                    related_name="addresses")
    street      = models.CharField(max_length=500, null=True, blank=True)
    postal_code = models.CharField(max_length=20,  null=True, blank=True)
    city        = models.CharField(max_length=255,  null=True, blank=True)
    country     = models.CharField(max_length=255)
    metadata    = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "company_addresses"
        unique_together = [("company", "street", "postal_code", "city", "country")]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["city", "country"]),
        ]

    def __str__(self):
        return f"{self.city}, {self.country}"


class CompanyDescription(models.Model):
    """
    A company can have many descriptions extracted from different documents.
    """
    company                 = models.ForeignKey(Company,    on_delete=models.CASCADE,
                                                related_name="descriptions")
    document                = models.ForeignKey("Document", on_delete=models.CASCADE,
                                                related_name="company_descriptions")
    description             = models.TextField()
    normalized_description  = models.TextField(null=True, blank=True)
    metadata                = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "company_descriptions"
        indexes  = [
            models.Index(fields=["company"]),
            models.Index(fields=["document"]),
            models.Index(fields=["company", "document"]),
        ]


class CompanyProfileCache(models.Model):
    """
    Read model / pre-computed JSON profile for fast dashboard rendering.
    Cache only — not the source of truth.
    """
    company          = models.OneToOneField(Company, on_delete=models.CASCADE,
                                            primary_key=True, related_name="profile_cache")
    profile_json     = models.JSONField()
    last_refreshed_at = models.DateTimeField()

    class Meta:
        managed  = False
        db_table = "company_profile_cache"
        indexes  = [models.Index(fields=["last_refreshed_at"])]


# ════════════════════════════════════════════════════════════
# CONTACT DATA ENTITIES
# ════════════════════════════════════════════════════════════

class Phone(models.Model):
    country_dial_code        = models.CharField(max_length=10,  null=True, blank=True)
    phone_number             = models.CharField(max_length=50)
    full_phone_number        = models.CharField(max_length=60,  null=True, blank=True)
    normalized_phone_number  = models.CharField(max_length=60,  null=True, blank=True)
    phone_type               = models.ForeignKey(PhoneType, on_delete=models.PROTECT,
                                                 related_name="phones")
    metadata                 = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "phones"
        unique_together = [("full_phone_number", "phone_type")]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["full_phone_number"]),
            models.Index(fields=["normalized_phone_number"]),
            models.Index(fields=["phone_type"]),
        ]

    def __str__(self):
        return self.full_phone_number or self.phone_number


class Email(models.Model):
    email_address            = models.EmailField(unique=True)
    normalized_email_address = models.CharField(max_length=255, null=True, blank=True)
    is_professional          = models.BooleanField()
    metadata                 = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "emails"
        indexes  = [
            models.Index(fields=["email_address"]),
            models.Index(fields=["normalized_email_address"]),
            models.Index(fields=["is_professional"]),
        ]

    def __str__(self):
        return self.email_address


class Website(models.Model):
    url            = models.URLField(unique=True, max_length=500)
    normalized_url = models.CharField(max_length=500, null=True, blank=True)
    website_type   = models.CharField(max_length=50, null=True, blank=True)
    description    = models.TextField(null=True, blank=True)
    metadata       = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "websites"
        indexes  = [
            models.Index(fields=["url"]),
            models.Index(fields=["normalized_url"]),
            models.Index(fields=["website_type"]),
        ]

    def __str__(self):
        return self.url


class SocialNetworkAccount(models.Model):
    social_network_type    = models.ForeignKey(SocialNetworkType, on_delete=models.PROTECT,
                                               related_name="accounts")
    account_value          = models.CharField(max_length=255)
    normalized_account_value = models.CharField(max_length=255, null=True, blank=True)
    profile_url            = models.URLField(max_length=500, null=True, blank=True)
    metadata               = models.JSONField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = "social_network_accounts"
        unique_together = [("social_network_type", "account_value")]
        indexes = [
            models.Index(fields=["social_network_type"]),
            models.Index(fields=["account_value"]),
            models.Index(fields=["normalized_account_value"]),
        ]

    def __str__(self):
        return f"{self.social_network_type.code}: {self.account_value}"


# ════════════════════════════════════════════════════════════
# DOCUMENT ENTITIES
# ════════════════════════════════════════════════════════════

class Document(models.Model):
    trade_show       = models.ForeignKey(TradeShow,    on_delete=models.PROTECT,
                                         related_name="documents")
    document_type    = models.ForeignKey(DocumentType, on_delete=models.PROTECT,
                                         related_name="documents")
    file_name        = models.CharField(max_length=500, null=True, blank=True)
    file_hash        = models.CharField(max_length=64,  unique=True, null=True, blank=True)
    page_count       = models.IntegerField(null=True, blank=True)
    ingestion_status = models.CharField(max_length=50,  null=True, blank=True)
    ingested_at      = models.DateTimeField(null=True, blank=True)
    ocr_engine_version = models.CharField(max_length=50, null=True, blank=True)
    metadata         = models.JSONField(null=True, blank=True)

    languages = models.ManyToManyField(Language, through="DocumentLanguage",
                                       related_name="documents")

    class Meta:
        managed  = False
        db_table = "documents"
        indexes  = [
            models.Index(fields=["trade_show"]),
            models.Index(fields=["document_type"]),
            models.Index(fields=["trade_show", "document_type"]),
            models.Index(fields=["file_hash"]),
            models.Index(fields=["ingestion_status"]),
            models.Index(fields=["ingested_at"]),
        ]

    def __str__(self):
        return self.file_name or str(self.id)


class DocumentLanguage(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "document_languages"
        unique_together = [("document", "language")]


# ════════════════════════════════════════════════════════════
# JUNCTION / THROUGH TABLES
# ════════════════════════════════════════════════════════════

class TradeShowSector(models.Model):
    trade_show = models.ForeignKey(TradeShow, on_delete=models.CASCADE)
    sector     = models.ForeignKey(Sector,    on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "trade_show_sectors"
        unique_together = [("trade_show", "sector")]


class CompanySector(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    sector  = models.ForeignKey(Sector,  on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_sectors"
        unique_together = [("company", "sector")]


class CompanyDoc(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    company  = models.ForeignKey(Company,  on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_docs"
        unique_together = [("document", "company")]


class CompanyPhone(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    phone   = models.ForeignKey(Phone,   on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_phones"
        unique_together = [("company", "phone")]


class CompanyContactPhone(models.Model):
    company_contact = models.ForeignKey(CompanyContact, on_delete=models.CASCADE)
    phone           = models.ForeignKey(Phone,          on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_contact_phones"
        unique_together = [("company_contact", "phone")]


class CompanyEmail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    email   = models.ForeignKey(Email,   on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_emails"
        unique_together = [("company", "email")]


class CompanyContactEmail(models.Model):
    company_contact = models.ForeignKey(CompanyContact, on_delete=models.CASCADE)
    email           = models.ForeignKey(Email,          on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_contact_emails"
        unique_together = [("company_contact", "email")]


class CompanyWebsite(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_websites"
        unique_together = [("company", "website")]


class CompanySocialNetwork(models.Model):
    company                = models.ForeignKey(Company,              on_delete=models.CASCADE)
    social_network_account = models.ForeignKey(SocialNetworkAccount, on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_social_networks"
        unique_together = [("company", "social_network_account")]


class CompanyContactSocialNetwork(models.Model):
    company_contact        = models.ForeignKey(CompanyContact,       on_delete=models.CASCADE)
    social_network_account = models.ForeignKey(SocialNetworkAccount, on_delete=models.CASCADE)

    class Meta:
        managed  = False
        db_table = "company_contact_social_networks"
        unique_together = [("company_contact", "social_network_account")]


# ════════════════════════════════════════════════════════════
# PROVENANCE / ORIGIN TABLES
# ════════════════════════════════════════════════════════════

class OriginDocBase(models.Model):
    """Abstract base for all *_origin_docs tables."""
    document           = models.ForeignKey(Document, on_delete=models.CASCADE)
    page_number        = models.IntegerField(null=True, blank=True)
    raw_text           = models.TextField(null=True, blank=True)
    confidence_score   = models.DecimalField(max_digits=4, decimal_places=3,
                                             null=True, blank=True)
    extraction_engine  = models.CharField(max_length=100, null=True, blank=True)
    extracted_at       = models.DateTimeField(null=True, blank=True)
    metadata           = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True


class PhoneOriginDoc(OriginDocBase):
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, related_name="origin_docs")

    class Meta:
        managed  = False
        db_table = "phone_origin_docs"
        unique_together = [("document", "phone")]


class AddressOriginDoc(OriginDocBase):
    company_address = models.ForeignKey(CompanyAddress, on_delete=models.CASCADE,
                                        related_name="origin_docs")

    class Meta:
        managed  = False
        db_table = "address_origin_docs"
        unique_together = [("document", "company_address")]


class WebsiteOriginDoc(OriginDocBase):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="origin_docs")

    class Meta:
        managed  = False
        db_table = "website_origin_docs"
        unique_together = [("document", "website")]


class EmailOriginDoc(OriginDocBase):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="origin_docs")

    class Meta:
        managed  = False
        db_table = "email_origin_docs"
        unique_together = [("document", "email")]


class ContactOriginDoc(OriginDocBase):
    company_contact = models.ForeignKey(CompanyContact, on_delete=models.CASCADE,
                                        related_name="origin_docs")

    class Meta:
        managed  = False
        db_table = "contact_origin_docs"
        unique_together = [("document", "company_contact")]


class SocialNetworkOriginDoc(OriginDocBase):
    social_network_account = models.ForeignKey(SocialNetworkAccount, on_delete=models.CASCADE,
                                               related_name="origin_docs")

    class Meta:
        managed  = False
        db_table = "social_network_origin_docs"
        unique_together = [("document", "social_network_account")]

