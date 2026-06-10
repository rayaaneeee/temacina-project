from django.urls import path
from . import views

urlpatterns = [
    # ── Trade Shows ─────────────────────────────────────
    path("trade-shows/", views.TradeShowListView.as_view(), name="trade-show-list"),
    path("trade-shows/<int:pk>/", views.TradeShowDetailView.as_view(), name="trade-show-detail"),
    path("trade-shows/<int:pk>/stats/", views.TradeShowStatsView.as_view(), name="trade-show-stats"),
    path("trade-shows/<int:pk>/ingestion-progress/", views.DocumentIngestionProgressView.as_view(), name="trade-show-ingestion-progress"),

    # ── Sectors ────────────────────────────────────────
    path("sectors/", views.SectorListView.as_view(), name="sector-list"),

    # ── Contacts ──────────────────────────────────────
    path("contacts/", views.ContactListView.as_view(), name="contact-list"),

    # ── Companies ──────────────────────────────────────
    path("companies/", views.CompanyListView.as_view(), name="company-list"),
    path("companies/<int:pk>/", views.CompanyDetailView.as_view(), name="company-detail"),
    path("companies/<int:pk>/profile/", views.CompanyProfileCacheView.as_view(),
         name="company-profile"),
    path("companies/<int:pk>/phones/", views.CompanyPhonesView.as_view(),
         name="company-phones"),
    path("companies/<int:pk>/emails/", views.CompanyEmailsView.as_view(),
         name="company-emails"),
    path("companies/count-per-trade-show/",
         views.CompanyCountPerTradeShowView.as_view(),
         name="company-count-per-trade-show"),

    # ── Documents ─────────────────────────────────────
    path("documents/", views.DocumentListView.as_view(), name="document-list"),
    path("documents/<int:pk>/", views.DocumentDetailView.as_view(), name="document-detail"),
    path(
        "documents/<int:pk>/ingestion-progress/",
        views.DocumentIngestionProgressView.as_view(),
        name="document-ingestion-progress",
    ),

    # ── Dashboard analytics ───────────────────────────
    path("dashboard/kpis/", views.DashboardKPIView.as_view(), name="dashboard-kpis"),

    # ── Global search ─────────────────────────────────
    path("search/", views.GlobalSearchView.as_view(), name="global-search"),
]
