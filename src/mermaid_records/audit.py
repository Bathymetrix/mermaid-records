# SPDX-License-Identifier: MIT

"""Corpus audit helpers built on top of discovery and parsing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .discovery import iter_mer_files
from .mer_raw import parse_mer_file


@dataclass(slots=True)
class MerCorpusStats:
    """Summary counts for a corpus of raw .MER files."""

    total_files: int
    parsed_ok: int
    empty_files: int
    non_empty_files: int


def audit_server_mer(root: Path) -> MerCorpusStats:
    """Audit a server-style raw MER corpus rooted at ``root``."""

    total_files = 0
    parsed_ok = 0
    empty_files = 0
    non_empty_files = 0

    for path in iter_mer_files(root):
        total_files += 1
        _, blocks = parse_mer_file(path)
        parsed_ok += 1
        if len(blocks) == 0:
            empty_files += 1
        else:
            non_empty_files += 1

    return MerCorpusStats(
        total_files=total_files,
        parsed_ok=parsed_ok,
        empty_files=empty_files,
        non_empty_files=non_empty_files,
    )
