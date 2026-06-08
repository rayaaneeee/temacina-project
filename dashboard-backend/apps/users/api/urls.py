from django.urls import path
from . import views

urlpatterns = [
    # GET       /api/v1/users/me/                   own profile
    # PATCH     /api/v1/users/me/                   update own profile
    path("me/",                       views.MeView.as_view(),                name="user-me"),

    # GET       /api/v1/users/                      list users (admin+)
    # POST      /api/v1/users/                      create user (admin+)
    path("",                          views.UserListCreateView.as_view(),     name="user-list"),

    # GET       /api/v1/users/roles/                list all roles
    path("roles/",                    views.RoleListView.as_view(),           name="role-list"),

    # GET       /api/v1/users/sectors/              list all user sectors
    path("sectors/",                  views.UserSectorListView.as_view(),     name="user-sector-list"),

    # GET       /api/v1/users/{id}/                 user detail (manager+)
    # PATCH     /api/v1/users/{id}/                 update user
    # DELETE    /api/v1/users/{id}/                 deactivate user
    path("<int:pk>/",                 views.UserDetailView.as_view(),         name="user-detail"),

    # POST      /api/v1/users/{id}/role/            change role
    path("<int:pk>/role/",            views.ChangeRoleView.as_view(),         name="user-change-role"),

    # GET       /api/v1/users/{id}/reports/         direct reports
    path("<int:pk>/reports/",         views.DirectReportsView.as_view(),      name="user-reports"),

    # GET       /api/v1/users/{id}/sessions/        login history
    path("<int:pk>/sessions/",        views.UserSessionsView.as_view(),       name="user-sessions"),

    # POST      /api/v1/users/{id}/companies/       assign company
    # GET       /api/v1/users/{id}/companies/       list assigned companies
    path("<int:pk>/companies/",       views.UserAssignedCompaniesView.as_view(),
         name="user-companies"),
    path("<int:pk>/companies/assign/",views.AssignCompanyView.as_view(),
         name="user-assign-company"),
]
