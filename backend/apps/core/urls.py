from django.urls import path
from . import views
from .views import DashboardView
# add this to urlpatterns:
path("dashboard/", DashboardView.as_view(), name="dashboard"),
urlpatterns = [
    path("organizations/", views.OrganizationListCreateView.as_view(), name="org-list"),
    path("organizations/<int:pk>/", views.OrganizationDetailView.as_view(), name="org-detail"),
    path("audit-logs/", views.AuditLogListView.as_view(), name="audit-logs"),
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
]