"""
services.py — Ingestion service.

Orchestrates:
1. Reading the uploaded file
2. Calling the right parser
3. Creating RawRecord for each row
4. Updating the UploadBatch status
"""
import json
from django.utils import timezone
from django.db import transaction

from .models import UploadBatch, RawRecord
from .parsers import get_parser, parse_travel_json
from apps.core.models import write_audit_log


def ingest_batch(batch: UploadBatch) -> None:
    """
    Main entry point for ingestion.
    Reads batch.original_file, parses it, stores RawRecords.
    """
    batch.status = "processing"
    batch.save(update_fields=["status"])

    try:
        source_type = batch.data_source.source_type
        file = batch.original_file

        file.open("rb")
        raw_bytes = file.read()
        file.close()

        rows = []

        if source_type in ("sap_csv", "utility_csv"):
            # Decode as UTF-8 (with fallback to latin-1 for SAP)
            try:
                content = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = raw_bytes.decode("latin-1")

            parser = get_parser(source_type)
            rows = list(parser(content))

        elif source_type == "travel_api":
            # Travel data comes as JSON array
            content = raw_bytes.decode("utf-8")
            data = json.loads(content)
            rows = list(parse_travel_json(data if isinstance(data, list) else [data]))

        else:
            raise ValueError(f"Unknown source_type: {source_type}")

        # Write all raw records in one transaction
        with transaction.atomic():
            raw_records = [
                RawRecord(
                    batch=batch,
                    organization=batch.organization,
                    row_number=i + 1,
                    raw_data=row,
                    source_type=source_type,
                    status="pending",
                )
                for i, row in enumerate(rows)
            ]
            RawRecord.objects.bulk_create(raw_records)

            batch.total_rows = len(rows)
            batch.processed_rows = len(rows)
            batch.status = "completed"
            batch.completed_at = timezone.now()
            batch.save()

        # Write audit log
        write_audit_log(
            organization=batch.organization,
            entity_type="UploadBatch",
            entity_id=batch.id,
            action="ingested",
            new_value={
                "source_type": source_type,
                "total_rows": len(rows),
                "filename": batch.original_filename,
            },
            changed_by=batch.uploaded_by,
        )

    except Exception as exc:
        batch.status = "failed"
        batch.error_message = str(exc)
        batch.save(update_fields=["status", "error_message"])
        raise