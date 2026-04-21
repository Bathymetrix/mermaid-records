# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from pathlib import Path

from mermaid_records._audit_normalized_outputs import (
    audit_rows,
    discover_nonempty_families,
    inspect_sample_row,
    sample_family_rows,
)


def test_discover_nonempty_families_counts_only_nonempty_jsonl_files(tmp_path: Path) -> None:
    instrument_dir = tmp_path / "452.020-P-0001"
    instrument_dir.mkdir()
    (instrument_dir / "log_battery_records.jsonl").write_text(
        json.dumps(
            {
                "raw_line": "1700000000:[MONITR,461]battery 15000mV,   12000uA",
                "message": "battery 15000mV,   12000uA",
                "voltage_mv": 15000,
                "current_ua": 12000,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (instrument_dir / "log_unclassified_records.jsonl").write_text("", encoding="utf-8")

    inventory = discover_nonempty_families(tmp_path)

    assert inventory == [
        type(inventory[0])(
            family="log_battery_records",
            rows=1,
            files=1,
            instruments=1,
        )
    ]


def test_sample_family_rows_covers_every_nonempty_family_and_keeps_stanford_mer_example(
    tmp_path: Path,
) -> None:
    _write_jsonl_rows(
        tmp_path / "452.020-P-0001" / "log_battery_records.jsonl",
        [
            {
                "raw_line": "1700000000:[MONITR,461]battery 15000mV,   12000uA",
                "message": "battery 15000mV,   12000uA",
                "voltage_mv": 15000,
                "current_ua": 12000,
                "log_epoch_time": "1700000000",
            }
        ],
    )
    _write_jsonl_rows(
        tmp_path / "452.020-P-0002" / "mer_event_records.jsonl",
        [
            {
                "raw_info_line": "<INFO DATE=2024-01-01T00:00:00 PRESSURE=1.00 TEMPERATURE=2.0000 CRITERION=3.0 SNR=4.0 TRIG=5 DETRIG=6 />",
                "raw_format_line": "<FORMAT ENDIANNESS=LITTLE BYTES_PER_SAMPLE=4 SAMPLING_RATE=20.000000 STAGES=5 NORMALIZED=YES LENGTH=2 />",
                "encoded_payload": "AAAAAA==",
                "encoded_payload_byte_count": 4,
                "data_payload_nbytes": 4,
                "event_info_date": "2024-01-01T00:00:00",
                "pressure": "1.00",
                "temperature": "2.0000",
                "criterion": "3.0",
                "snr": "4.0",
                "trig": "5",
                "detrig": "6",
                "endianness": "LITTLE",
                "bytes_per_sample": "4",
                "sampling_rate": "20.000000",
                "stages": "5",
                "normalized": "YES",
                "length": "2",
            }
        ],
    )
    _write_jsonl_rows(
        tmp_path / "465.152-R-0001" / "mer_event_records.jsonl",
        [
            {
                "raw_info_line": "<INFO DATE=2024-01-01T00:00:00 ROUNDS=468 />",
                "raw_format_line": None,
                "encoded_payload": "AAAAAA==",
                "encoded_payload_byte_count": 4,
                "data_payload_nbytes": 4,
                "event_info_date": "2024-01-01T00:00:00",
                "rounds": "468",
            }
        ],
    )

    samples = sample_family_rows(tmp_path, sample_per_family=1, seed=7)

    assert {sample.family for sample in samples} == {"log_battery_records", "mer_event_records"}
    assert any(sample.instrument_dir.startswith("465.152-R-") for sample in samples if sample.family == "mer_event_records")


def test_inspect_sample_row_reports_battery_mismatch(tmp_path: Path) -> None:
    _write_jsonl_rows(
        tmp_path / "452.020-P-0001" / "log_battery_records.jsonl",
        [
            {
                "raw_line": "1700000000:[MONITR,461]battery 15000mV,   12000uA",
                "message": "battery 15000mV,   12000uA",
                "voltage_mv": 14999,
                "current_ua": 12000,
                "log_epoch_time": "1700000000",
            }
        ],
    )

    sample = sample_family_rows(tmp_path, sample_per_family=1, seed=1)[0]

    assert inspect_sample_row(sample) == ["voltage_mv does not match the preserved raw_line value"]


def test_audit_rows_reports_findings_and_full_coverage(tmp_path: Path) -> None:
    _write_jsonl_rows(
        tmp_path / "452.020-P-0001" / "log_pressure_temperature_records.jsonl",
        [
            {
                "raw_line": "1700000000:[PRESS , 81]P  +1000mbar,T+2000mdegC",
                "message": "P  +1000mbar,T+2000mdegC",
                "pressure_mbar": 1000,
                "temperature_mdegc": 1999,
                "log_epoch_time": "1700000000",
            }
        ],
    )

    inventory = discover_nonempty_families(tmp_path)
    samples = sample_family_rows(tmp_path, sample_per_family=1, seed=3)
    report = audit_rows(samples, inventory)

    assert report["covered_every_nonempty_family"] is True
    assert report["release_blocking"] is True
    assert report["findings"][0]["family"] == "log_pressure_temperature_records"
    assert "temperature_mdegc does not match the preserved raw_line value" in report["findings"][0]["issues"]


def _write_jsonl_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
