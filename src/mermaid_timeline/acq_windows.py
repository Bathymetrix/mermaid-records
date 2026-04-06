"""Acquisition window helpers."""

from __future__ import annotations

from collections.abc import Iterable

from .models import AcquisitionWindow


def collect_acquisition_windows(
    windows: Iterable[AcquisitionWindow],
) -> list[AcquisitionWindow]:
    """Return acquisition windows as a concrete list."""

    return list(windows)
