#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Internal dev utility for randomized audits of normalized JSONL outputs."""

from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from mermaid_records._audit_normalized_outputs import main


if __name__ == "__main__":
    raise SystemExit(main())
