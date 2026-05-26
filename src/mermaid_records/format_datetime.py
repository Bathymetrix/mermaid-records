# SPDX-License-Identifier: MIT

"""Datetime parsing and formatting helpers for normalized outputs."""

from __future__ import annotations

from datetime import datetime, timezone


def parse_source_datetime(value: str) -> datetime:
    """Parse a source timestamp, preserving or assigning UTC timezone context."""

    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_utc_datetime(value: datetime) -> str:
    """Format a datetime as UTC ISO8601 with microseconds and a Z suffix."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def format_source_datetime(value: str | None) -> str | None:
    """Parse and format a source timestamp for normalized non-raw fields."""

    if value is None:
        return None
    return format_utc_datetime(parse_source_datetime(value))
