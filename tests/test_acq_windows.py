# SPDX-License-Identifier: MIT

from pathlib import Path

from mermaid_records.acq_windows import extract_acquisition_windows
from mermaid_records.operational_raw import iter_operational_log_entries


def test_extract_acquisition_windows_from_fixture() -> None:
    path = Path("data/fixtures/467.174-T-0100/log/0100_6858665E.LOG")
    windows = extract_acquisition_windows(iter_operational_log_entries(path))

    assert len(windows) >= 1
    assert windows[0].start.isoformat() == "2025-06-23T05:05:24"
    assert windows[0].stop.isoformat() == "2025-06-23T05:20:32"
