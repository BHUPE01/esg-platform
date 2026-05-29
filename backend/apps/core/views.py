from django.db.models import Count, Q
from django.contrib.auth.models import User

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.ingestion.models import RawRecord, UploadBatch
from apps.normalization.models import NormalizedRecord
from apps.validation.models import ValidationFlag

from .models import Organization, AuditLog
from .serializers import (
    OrganizationSerializer,
    AuditLogSerializer,
    UserSerializer,
)


class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrganizationDetailView(generics.RetrieveUpdateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = AuditLog.objects.select_related("changed_by")

        org_id = self.request.query_params.get("org")
        entity_type = self.request.query_params.get("entity_type")
        entity_id = self.request.query_params.get("entity_id")

        if org_id:
            qs = qs.filter(organization_id=org_id)

        if entity_type:
            qs = qs.filter(entity_type=entity_type)

        if entity_id:
            qs = qs.filter(entity_id=entity_id)

        return qs


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org_id = request.query_params.get("org")

        raw_qs = RawRecord.objects.all()
        norm_qs = NormalizedRecord.objects.all()
        flag_qs = ValidationFlag.objects.all()
        batch_qs = UploadBatch.objects.all()

        if org_id:
            raw_qs = raw_qs.filter(organization_id=org_id)
            norm_qs = norm_qs.filter(organization_id=org_id)
            flag_qs = flag_qs.filter(organization_id=org_id)
            batch_qs = batch_qs.filter(organization_id=org_id)

        review_counts = (
            norm_qs.values("review_status")
            .annotate(count=Count("id"))
        )

        review_map = {
            r["review_status"]: r["count"]
            for r in review_counts
        }

        source_counts = (
            norm_qs.values("source_type")
            .annotate(count=Count("id"))
        )

        return Response({
            "total_raw_records": raw_qs.count(),
            "total_normalized_records": norm_qs.count(),
            "total_upload_batches": batch_qs.count(),

            "pending_review": review_map.get("pending", 0),
            "flagged": review_map.get("flagged", 0),
            "approved": review_map.get("approved", 0),
            "rejected": review_map.get("rejected", 0),

            "open_flags": flag_qs.filter(
                status="open"
            ).count(),

            "error_flags": flag_qs.filter(
                severity="error",
                status="open"
            ).count(),

            "source_breakdown": list(source_counts),

            "recent_batches": [
                {
                    "id": b.id,
                    "source": b.data_source.name if b.data_source else None,
                    "status": b.status,
                    "total_rows": b.total_rows,
                    "created_at": b.created_at,
                }
                for b in batch_qs.order_by("-created_at")[:5]
            ],
        })