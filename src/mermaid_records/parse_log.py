# SPDX-License-Identifier: MIT

"""Parser interfaces for operational LOG text files."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Callable, Iterator

from .models import OperationalLogEntry

_LOG_LINE_RE = re.compile(
    r"^(?P<time>.+?):\[(?P<tag>[^\]]+)\](?P<message>.*)$"
)

type MalformedLogLineCallback = Callable[[int, str, str], None]


def iter_operational_log_entries(
    path: Path,
    *,
    on_malformed_line: MalformedLogLineCallback | None = None,
) -> Iterator[OperationalLogEntry]:
    """Yield parsed LOG lines as conservative structured entries."""

    _validate_log_path(path)

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\r\n")
            if not line.strip():
                continue
            match = _LOG_LINE_RE.match(line)
            if not match:
                _report_malformed_line(
                    on_malformed_line,
                    line_number=line_number,
                    raw_line=line,
                    error="line does not match expected LOG pattern",
                )
                continue
            try:
                tag = match.group("tag")
                subsystem, code = _parse_tag(tag)
                yield OperationalLogEntry(
                    time=_parse_time_text(match.group("time")),
                    subsystem=subsystem,
                    code=code,
                    message=match.group("message"),
                    source_kind="log",
                    raw_line=line,
                    source_file=path,
                )
            except Exception as exc:
                _report_malformed_line(
                    on_malformed_line,
                    line_number=line_number,
                    raw_line=line,
                    error=str(exc),
                )


def _parse_tag(tag: str) -> tuple[str, str | None]:
    """Split a bracket tag into subsystem and optional code."""

    if "," not in tag:
        return tag.strip(), None
    subsystem, code = tag.split(",", maxsplit=1)
    return subsystem.strip(), code.strip() or None


def _validate_log_path(path: Path) -> None:
    """Validate that the parser is being used on a LOG file."""

    if path.suffix.upper() != ".LOG":
        raise ValueError(f"Unsupported operational log source: {path}")


def _parse_time_text(text: str) -> datetime:
    """Parse either an epoch-seconds prefix or an ISO timestamp."""

    if text.isdigit():
        return datetime.fromtimestamp(int(text), tz=timezone.utc).replace(tzinfo=None)
    return datetime.fromisoformat(text)


def _report_malformed_line(
    callback: MalformedLogLineCallback | None,
    *,
    line_number: int,
    raw_line: str,
    error: str,
) -> None:
    if callback is not None:
        callback(line_number, raw_line, error)
