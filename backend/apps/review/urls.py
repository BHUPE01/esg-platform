from django.urls import path
from . import views

urlpatterns = [
    path("queue/", views.ReviewQueueView.as_view(), name="review-queue"),
    path("records/<int:pk>/approve/", views.ApproveRecordView.as_view(), name="approve"),
    path("records/<int:pk>/reject/", views.RejectRecordView.as_view(), name="reject"),
    path("records/<int:pk>/edit/", views.EditRecordView.as_view(), name="edit"),
]