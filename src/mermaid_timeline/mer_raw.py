"""Low-level interfaces for parsing raw MER files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from .models import MerRecord


def iter_mer_records(path: Path) -> Iterator[MerRecord]:
    """Yield conservative MER records while preserving raw payload bytes.

    This stub intentionally avoids format-specific decoding. Each non-empty
    line is surfaced as a generic record so higher-level interpretation can
    evolve independently from raw parsing.
    """

    with path.open("rb") as handle:
        offset = 0
        for raw_line in handle:
            payload = raw_line.rstrip(b"\r\n")
            if not payload:
                offset += len(raw_line)
                continue
            yield MerRecord(offset=offset, payload=payload)
            offset += len(raw_line)
