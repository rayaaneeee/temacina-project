from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # POST  /api/v1/auth/login/
    path("login/",            views.LoginView.as_view(),               name="auth-login"),
    # POST  /api/v1/auth/logout/
    path("logout/",           views.LogoutView.as_view(),              name="auth-logout"),
    # POST  /api/v1/auth/refresh/
    path("refresh/",          TokenRefreshView.as_view(),              name="auth-refresh"),
    # POST  /api/v1/auth/password/change/
    path("password/change/",  views.ChangePasswordView.as_view(),      name="auth-change-password"),
    # POST  /api/v1/auth/password/reset/
    path("password/reset/",   views.PasswordResetRequestView.as_view(),name="auth-reset-request"),
    # POST  /api/v1/auth/password/reset/confirm/
    path("password/reset/confirm/", views.PasswordResetConfirmView.as_view(),
         name="auth-reset-confirm"),
]
