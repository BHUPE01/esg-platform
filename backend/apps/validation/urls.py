from django.urls import path
from . import views

urlpatterns = [
    path("rules/", views.ValidationRuleListCreateView.as_view(), name="rule-list"),
    path("flags/", views.ValidationFlagListView.as_view(), name="flag-list"),
    path("flags/<int:pk>/resolve/", views.ResolveFlagView.as_view(), name="flag-resolve"),
    path("validate-batch/", views.ValidateBatchView.as_view(), name="validate-batch"),
]