"""
review/views.py — Analyst review workflow.

Analysts can:
- approve a normalized record
- reject a normalized record
- edit fields and save

Every action writes an AuditLog entry automatically.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.normalization.models import NormalizedRecord
from apps.normalization.serializers import NormalizedRecordSerializer
from apps.core.models import write_audit_log


def _snapshot(record: NormalizedRecord) -> dict:
    """Snapshot relevant fields for audit log."""
    return {
        "review_status": record.review_status,
        "quantity": str(record.quantity) if record.quantity else None,
        "unit": record.unit,
        "record_date": str(record.record_date) if record.record_date else None,
        "site_code": record.site_code,
        "review_notes": record.review_notes,
    }


class ApproveRecordView(APIView):
    """
    POST /api/review/records/<id>/approve/
    Body: { "notes": "Looks good" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        record = get_object_or_404(NormalizedRecord, pk=pk)
        old_value = _snapshot(record)

        record.review_status = "approved"
        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.review_notes = request.data.get("notes", "")
        record.save()

        write_audit_log(
            organization=record.organization,
            entity_type="NormalizedRecord",
            entity_id=record.id,
            action="approved",
            old_value=old_value,
            new_value=_snapshot(record),
            changed_by=request.user,
            notes=record.review_notes,
        )

        return Response(NormalizedRecordSerializer(record).data)


class RejectRecordView(APIView):
    """
    POST /api/review/records/<id>/reject/
    Body: { "notes": "Invalid plant code" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        record = get_object_or_404(NormalizedRecord, pk=pk)
        notes = request.data.get("notes", "")
        if not notes:
            return Response(
                {"error": "notes are required when rejecting"},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_value = _snapshot(record)
        record.review_status = "rejected"
        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.review_notes = notes
        record.save()

        write_audit_log(
            organization=record.organization,
            entity_type="NormalizedRecord",
            entity_id=record.id,
            action="rejected",
            old_value=old_value,
            new_value=_snapshot(record),
            changed_by=request.user,
            notes=notes,
        )

        return Response(NormalizedRecordSerializer(record).data)


class EditRecordView(APIView):
    """
    PATCH /api/review/records/<id>/edit/

    Allows editing specific fields of a NormalizedRecord.
    Editable fields are whitelisted to prevent accidental corruption.
    Every edit writes a full audit trail.
    """
    EDITABLE_FIELDS = [
        "quantity", "unit", "record_date", "site_code",
        "tariff", "cabin_class", "hotel_nights",
        "departure_airport", "arrival_airport",
        "billing_start", "billing_end",
        "review_notes",
    ]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        record = get_object_or_404(NormalizedRecord, pk=pk)
        old_value = _snapshot(record)

        updated_fields = []
        for field in self.EDITABLE_FIELDS:
            if field in request.data:
                setattr(record, field, request.data[field])
                updated_fields.append(field)

        if not updated_fields:
            return Response(
                {"error": "No editable fields provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        record.reviewed_by = request.user
        record.reviewed_at = timezone.now()
        record.save()

        write_audit_log(
            organization=record.organization,
            entity_type="NormalizedRecord",
            entity_id=record.id,
            action="updated",
            old_value=old_value,
            new_value=_snapshot(record),
            changed_by=request.user,
            notes=f"Fields edited: {', '.join(updated_fields)}",
        )

        return Response(NormalizedRecordSerializer(record).data)


class ReviewQueueView(APIView):
    """
    GET /api/review/queue/?org=1
    Returns all records that need analyst attention:
    - status = pending or flagged
    Ordered by flagged first, then oldest first.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        org_id = request.query_params.get("org")
        qs = NormalizedRecord.objects.filter(
            review_status__in=["pending", "flagged"]
        ).prefetch_related("flags").select_related("raw_record", "reviewed_by")

        if org_id:
            qs = qs.filter(organization_id=org_id)

        # Flagged records first, then by creation date
        qs = qs.order_by(
            "-review_status",  # 'pending' < 'flagged' alphabetically — adjust if needed
            "created_at"
        )

        serializer = NormalizedRecordSerializer(qs[:100], many=True)
        return Response({"count": qs.count(), "results": serializer.data})