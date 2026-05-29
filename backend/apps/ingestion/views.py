from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import DataSource, UploadBatch, RawRecord
from .serializers import (
    DataSourceSerializer,
    UploadBatchSerializer,
    RawRecordSerializer,
)
from .services import ingest_batch
from apps.core.models import Organization


class DataSourceListCreateView(generics.ListCreateAPIView):
    serializer_class = DataSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.query_params.get("org")
        qs = DataSource.objects.filter(is_active=True)
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return qs

    def perform_create(self, serializer):
        org_id = self.request.data.get("organization")
        org = get_object_or_404(Organization, id=org_id)
        serializer.save(organization=org)


class UploadBatchListView(generics.ListAPIView):
    serializer_class = UploadBatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = UploadBatch.objects.select_related("data_source", "uploaded_by")
        org_id = self.request.query_params.get("org")
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return qs


class FileUploadView(APIView):
    """
    POST /api/ingestion/upload/
    Accepts a multipart file + data_source_id.
    Creates the UploadBatch and runs ingestion synchronously.
    (In production, you'd push ingestion to a background task.)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data_source_id = request.data.get("data_source_id")
        file = request.FILES.get("file")

        if not data_source_id or not file:
            return Response(
                {"error": "data_source_id and file are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data_source = get_object_or_404(DataSource, id=data_source_id)

        batch = UploadBatch.objects.create(
            organization=data_source.organization,
            data_source=data_source,
            uploaded_by=request.user,
            original_file=file,
            original_filename=file.name,
            status="pending",
        )

        try:
            ingest_batch(batch)
        except Exception as e:
            return Response(
                {"error": str(e), "batch_id": batch.id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = UploadBatchSerializer(batch)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RawRecordListView(generics.ListAPIView):
    serializer_class = RawRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = RawRecord.objects.all()
        batch_id = self.request.query_params.get("batch")
        org_id = self.request.query_params.get("org")
        record_status = self.request.query_params.get("status")

        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if org_id:
            qs = qs.filter(organization_id=org_id)
        if record_status:
            qs = qs.filter(status=record_status)
        return qs