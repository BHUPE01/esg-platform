from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import NormalizedRecord
from .serializers import NormalizedRecordSerializer
from .services import normalize_batch


class NormalizedRecordListView(generics.ListAPIView):
    serializer_class = NormalizedRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = NormalizedRecord.objects.select_related(
            "raw_record", "reviewed_by"
        )
        org_id = self.request.query_params.get("org")
        review_status = self.request.query_params.get("review_status")
        source_type = self.request.query_params.get("source_type")

        if org_id:
            qs = qs.filter(organization_id=org_id)
        if review_status:
            qs = qs.filter(review_status=review_status)
        if source_type:
            qs = qs.filter(source_type=source_type)
        return qs


class NormalizedRecordDetailView(generics.RetrieveAPIView):
    queryset = NormalizedRecord.objects.select_related("raw_record", "reviewed_by")
    serializer_class = NormalizedRecordSerializer
    permission_classes = [permissions.IsAuthenticated]


class NormalizeBatchView(APIView):
    """
    POST /api/normalization/normalize-batch/
    Body: { "batch_id": 1 }
    Triggers normalization for all pending records in a batch.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        batch_id = request.data.get("batch_id")
        if not batch_id:
            return Response(
                {"error": "batch_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        result = normalize_batch(int(batch_id))
        return Response(result, status=status.HTTP_200_OK)