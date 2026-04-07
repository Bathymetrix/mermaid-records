"""Recursive discovery of raw MERMAID input files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

RAW_PATTERNS = {
    "cycle": "*.CYCLE.h",
    "mer": "*.MER",
}


def iter_cycle_files(root: Path) -> Iterator[Path]:
    """Recursively yield all .CYCLE.h files under root."""

    yield from iter_raw_inputs(root, kinds=("cycle",))


def iter_mer_files(root: Path) -> Iterator[Path]:
    """Recursively yield all .MER files under root."""

    yield from iter_raw_inputs(root, kinds=("mer",))


def iter_raw_inputs(
    root: Path,
    *,
    kinds: tuple[str, ...] = ("cycle", "mer"),
    sort: bool = False,
) -> Iterator[Path]:
    """Recursively yield raw input files under root."""

    _validate_root(root)
    patterns = [RAW_PATTERNS[kind] for kind in kinds]
    paths = _iter_matches(root, patterns)

    if sort:
        yield from sorted(paths)
    else:
        yield from paths


def _validate_root(root: Path) -> None:
    """Validate that root exists and is a directory."""

    if not root.exists():
        raise FileNotFoundError(root)
    if not root.is_dir():
        raise NotADirectoryError(root)


def _iter_matches(root: Path, patterns: list[str]) -> Iterator[Path]:
    """Yield all recursive matches for the given glob patterns."""

    for pattern in patterns:
        yield from root.rglob(pattern)
