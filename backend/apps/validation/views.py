from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ValidationRule, ValidationFlag
from .serializers import ValidationRuleSerializer, ValidationFlagSerializer
from .services import validate_batch, validate_record
from apps.normalization.models import NormalizedRecord


class ValidationRuleListCreateView(generics.ListCreateAPIView):
    serializer_class = ValidationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ValidationRule.objects.all()
        org_id = self.request.query_params.get("org")
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return qs

    def perform_create(self, serializer):
        from apps.core.models import Organization
        org_id = self.request.data.get("organization")
        org = get_object_or_404(Organization, id=org_id)
        serializer.save(organization=org)


class ValidationFlagListView(generics.ListAPIView):
    serializer_class = ValidationFlagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ValidationFlag.objects.select_related("normalized_record", "rule")
        org_id = self.request.query_params.get("org")
        flag_status = self.request.query_params.get("status")
        severity = self.request.query_params.get("severity")

        if org_id:
            qs = qs.filter(organization_id=org_id)
        if flag_status:
            qs = qs.filter(status=flag_status)
        if severity:
            qs = qs.filter(severity=severity)
        return qs


class ValidateBatchView(APIView):
    """
    POST /api/validation/validate-batch/
    Body: { "batch_id": 1 }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        batch_id = request.data.get("batch_id")
        if not batch_id:
            return Response({"error": "batch_id required"}, status=400)
        result = validate_batch(int(batch_id))
        return Response(result)


class ResolveFlagView(APIView):
    """
    POST /api/validation/flags/<id>/resolve/
    Body: { "status": "resolved"|"dismissed", "resolution_notes": "..." }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        flag = get_object_or_404(ValidationFlag, pk=pk)
        new_status = request.data.get("status")
        if new_status not in ("resolved", "dismissed"):
            return Response({"error": "status must be resolved or dismissed"}, status=400)
        flag.status = new_status
        flag.resolution_notes = request.data.get("resolution_notes", "")
        flag.save()
        return Response(ValidationFlagSerializer(flag).data)