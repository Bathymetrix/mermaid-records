"""Decode boundary for upstream raw inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator


def iter_decoded_cycle_lines(path: Path) -> Iterator[str]:
    """Yield decoded cycle text lines from one upstream raw .BIN file.

    This is the intended abstraction boundary between upstream decode and
    downstream parsing:

    - input: one raw `.BIN` file
    - output: decoded cycle-like text lines

    The decoder should eventually encapsulate the existing preprocess-style
    BIN-to-cycle transformation without forcing on-disk `.CYCLE` or `.CYCLE.h`
    emission. Parsing of decoded lines should remain a separate concern.
    """

    raise NotImplementedError("BIN decode is not implemented yet.")
