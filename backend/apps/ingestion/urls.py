from django.urls import path
from . import views

urlpatterns = [
    path("data-sources/", views.DataSourceListCreateView.as_view(), name="datasource-list"),
    path("upload/", views.FileUploadView.as_view(), name="upload"),
    path("batches/", views.UploadBatchListView.as_view(), name="batch-list"),
    path("raw-records/", views.RawRecordListView.as_view(), name="raw-records"),
]