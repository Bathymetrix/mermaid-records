# SPDX-License-Identifier: MIT

"""Legacy compatibility shims for CYCLE-oriented parser imports."""

from __future__ import annotations

from .operational_raw import iter_cycle_events, iter_operational_log_entries

__all__ = ["iter_cycle_events", "iter_operational_log_entries"]
