"""
parsers.py — Source-specific CSV parsers.

Each parser reads a file and yields dicts of raw row data.
They do NOT clean or validate — that's the normalizer's job.
They just faithfully read what's there.
"""
import csv
import io
from typing import Iterator


def parse_sap_csv(file_content: str) -> Iterator[dict]:
    """
    Reads SAP-style CSV with ugly column names.
    Handles BOM, semicolons vs commas, extra whitespace.
    Yields each row as a raw dict.
    """
    # Strip BOM if present (common in SAP exports)
    if file_content.startswith("\ufeff"):
        file_content = file_content[1:]

    # SAP exports sometimes use semicolons
    sample = file_content[:500]
    delimiter = ";" if sample.count(";") > sample.count(",") else ","

    reader = csv.DictReader(io.StringIO(file_content), delimiter=delimiter)
    for row in reader:
        # Strip whitespace from keys and values
        cleaned = {k.strip(): v.strip() for k, v in row.items() if k}
        if any(cleaned.values()):  # Skip fully empty rows
            yield cleaned


def parse_utility_csv(file_content: str) -> Iterator[dict]:
    """
    Reads utility electricity CSV.
    Expected columns: meter_id, billing_start, billing_end, kwh, tariff
    """
    if file_content.startswith("\ufeff"):
        file_content = file_content[1:]

    reader = csv.DictReader(io.StringIO(file_content))
    for row in reader:
        cleaned = {k.strip(): v.strip() for k, v in row.items() if k}
        if any(cleaned.values()):
            yield cleaned


def parse_travel_json(data: list) -> Iterator[dict]:
    """
    Reads mock travel API response (list of dicts).
    Expected fields: traveler, departure_airport, arrival_airport,
                     cabin_class, hotel_nights
    """
    for record in data:
        if isinstance(record, dict):
            yield record


def get_parser(source_type: str):
    """
    Returns the right parser function for a source type.
    """
    parsers = {
        "sap_csv": parse_sap_csv,
        "utility_csv": parse_utility_csv,
    }
    return parsers.get(source_type)