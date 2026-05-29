from django.urls import path
from . import views

urlpatterns = [
    path("records/", views.NormalizedRecordListView.as_view(), name="normalized-list"),
    path("records/<int:pk>/", views.NormalizedRecordDetailView.as_view(), name="normalized-detail"),
    path("normalize-batch/", views.NormalizeBatchView.as_view(), name="normalize-batch"),
]