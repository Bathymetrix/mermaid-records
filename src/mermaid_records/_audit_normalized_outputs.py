# SPDX-License-Identifier: MIT

"""Audit helper for randomized parsed-vs-raw checks on normalized JSONL outputs."""

from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import random
import re
from typing import Any


BATTERY_PATTERN = re.compile(r"battery\s+(-?\d+)mV,\s*(-?\d+)uA")
PRESSURE_TEMPERATURE_PATTERN = re.compile(r"P\s*([+-]?\d+)mbar,T\s*([+-]?\d+)mdegC")
ACQUISITION_MESSAGES = {
    "acq started": ("started", "transition"),
    "acq stopped": ("stopped", "transition"),
    "acq already started": ("started", "assertion"),
    "acq already stopped": ("stopped", "assertion"),
}


@dataclass(frozen=True, slots=True)
class FamilyInventoryRow:
    """Inventory summary for one non-empty normalized output family."""

    family: str
    rows: int
    files: int
    instruments: int


@dataclass(frozen=True, slots=True)
class FileSample:
    """One randomly chosen row from a concrete family file."""

    family: str
    instrument_dir: str
    path: Path
    row_count: int
    sample_line_num: int
    sample_row: dict[str, Any]


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the audit utility argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Perform a bounded randomized audit of normalized JSONL outputs by comparing "
            "parsed fields with preserved raw source content."
        )
    )
    parser.add_argument(
        "--records-root",
        type=Path,
        required=True,
        help="Root directory containing per-instrument normalized JSONL output folders.",
    )
    parser.add_argument(
        "--sample-per-family",
        type=int,
        default=3,
        help="Maximum number of sampled files to inspect for each non-empty family.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260421,
        help="Random seed used for reproducible bounded sampling.",
    )
    parser.add_argument(
        "--json",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Emit the full report as JSON instead of the console summary.",
    )
    return parser


def discover_nonempty_families(records_root: Path) -> list[FamilyInventoryRow]:
    """Return a compact inventory of every non-empty JSONL family under the output root."""

    family_rows: Counter[str] = Counter()
    family_files: Counter[str] = Counter()
    family_instruments: defaultdict[str, set[str]] = defaultdict(set)
    for instrument_dir in _iter_instrument_dirs(records_root):
        for path in sorted(instrument_dir.glob("*.jsonl")):
            if path.stat().st_size == 0:
                continue
            family = path.stem
            family_files[family] += 1
            family_instruments[family].add(instrument_dir.name)
            family_rows[family] += _count_jsonl_rows(path)
    return [
        FamilyInventoryRow(
            family=family,
            rows=family_rows[family],
            files=family_files[family],
            instruments=len(family_instruments[family]),
        )
        for family in sorted(family_rows)
    ]


def sample_family_rows(
    records_root: Path,
    *,
    sample_per_family: int,
    seed: int,
) -> list[FileSample]:
    """Select bounded representative samples across all non-empty families."""

    rng = random.Random(seed)
    samples_by_family: defaultdict[str, list[FileSample]] = defaultdict(list)
    for instrument_dir in _iter_instrument_dirs(records_root):
        for path in sorted(instrument_dir.glob("*.jsonl")):
            if path.stat().st_size == 0:
                continue
            sample = _sample_file_row(path, instrument_dir.name, rng)
            if sample is not None:
                samples_by_family[sample.family].append(sample)

    sampled: list[FileSample] = []
    for family, file_samples in sorted(samples_by_family.items()):
        chosen = _choose_distinct_instruments(file_samples, sample_per_family, rng)
        sampled.extend(chosen)

    sampled = _ensure_stanford_mer_example(sampled, samples_by_family, rng)
    return sorted(sampled, key=lambda sample: (sample.family, sample.instrument_dir, sample.path.as_posix()))


def audit_rows(samples: list[FileSample], inventory: list[FamilyInventoryRow]) -> dict[str, Any]:
    """Run family-specific parsed-vs-raw checks over sampled rows and summarize the result."""

    findings = []
    touched_instruments = sorted({sample.instrument_dir for sample in samples})
    sampled_families = sorted({sample.family for sample in samples})
    inventory_families = [row.family for row in inventory]
    for sample in samples:
        issues = inspect_sample_row(sample)
        if not issues:
            continue
        findings.append(
            {
                "path": sample.path.as_posix(),
                "family": sample.family,
                "instrument_dir": sample.instrument_dir,
                "sample_line_num": sample.sample_line_num,
                "row_detail": _finding_row_detail(sample.sample_row),
                "issues": issues,
            }
        )

    return {
        "inventory": [
            {
                "family": row.family,
                "rows": row.rows,
                "files": row.files,
                "instruments": row.instruments,
            }
            for row in inventory
        ],
        "sampled_families": sampled_families,
        "touched_instruments": touched_instruments,
        "covered_every_nonempty_family": sampled_families == inventory_families,
        "samples": [
            {
                "family": sample.family,
                "instrument_dir": sample.instrument_dir,
                "path": sample.path.as_posix(),
                "row_count": sample.row_count,
                "sample_line_num": sample.sample_line_num,
            }
            for sample in samples
        ],
        "findings": findings,
        "confidence": _confidence_label(findings, len(samples)),
        "release_blocking": bool(findings),
    }


def inspect_sample_row(sample: FileSample) -> list[str]:
    """Return concise issue strings for one sampled row."""

    row = sample.sample_row
    family = sample.family
    issues: list[str] = []
    if family.startswith("log_") and "raw_line" in row:
        raw_line = row["raw_line"]
        if row.get("log_epoch_time") and not raw_line.startswith(str(row["log_epoch_time"])):
            issues.append("log_epoch_time does not match the raw_line prefix")
        if row.get("message") and row["message"] not in raw_line:
            issues.append("message is not preserved verbatim within raw_line")

    if family == "log_battery_records":
        issues.extend(_check_log_battery_row(row))
    elif family == "log_pressure_temperature_records":
        issues.extend(_check_log_pressure_temperature_row(row))
    elif family == "log_acquisition_records":
        issues.extend(_check_log_acquisition_row(row))
    elif family == "log_ascent_request_records":
        issues.extend(_check_log_ascent_request_row(row))
    elif family in {"log_parameter_records", "log_testmode_records", "log_sbe_records"}:
        issues.extend(_check_grouped_log_row(row))
    elif family == "log_transmission_records":
        issues.extend(_check_log_transmission_row(row))
    elif family == "mer_environment_records":
        issues.extend(_check_mer_environment_row(row))
    elif family == "mer_parameter_records":
        issues.extend(_check_mer_parameter_row(row))
    elif family == "mer_event_records":
        issues.extend(_check_mer_event_row(row))
    return issues


def main(argv: list[str] | None = None) -> int:
    """Run the normalized-output audit helper."""

    args = build_argument_parser().parse_args(argv)
    records_root = args.records_root.expanduser().resolve()
    inventory = discover_nonempty_families(records_root)
    samples = sample_family_rows(
        records_root,
        sample_per_family=args.sample_per_family,
        seed=args.seed,
    )
    report = audit_rows(samples, inventory)
    report["records_root"] = records_root.as_posix()
    report["seed"] = args.seed
    report["sample_per_family"] = args.sample_per_family
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_format_console_summary(report))
    return 0 if not report["release_blocking"] else 1


def _iter_instrument_dirs(records_root: Path) -> list[Path]:
    return sorted(path for path in records_root.iterdir() if path.is_dir())


def _count_jsonl_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


def _sample_file_row(path: Path, instrument_dir: str, rng: random.Random) -> FileSample | None:
    chosen_line_num = 0
    chosen_row: dict[str, Any] | None = None
    row_count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_num, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row_count += 1
            if rng.randrange(row_count) == 0:
                chosen_line_num = line_num
                chosen_row = json.loads(line)
    if chosen_row is None:
        return None
    return FileSample(
        family=path.stem,
        instrument_dir=instrument_dir,
        path=path,
        row_count=row_count,
        sample_line_num=chosen_line_num,
        sample_row=chosen_row,
    )


def _choose_distinct_instruments(
    file_samples: list[FileSample],
    sample_per_family: int,
    rng: random.Random,
) -> list[FileSample]:
    if len(file_samples) <= sample_per_family:
        return sorted(file_samples, key=lambda sample: (sample.instrument_dir, sample.path.as_posix()))
    shuffled = file_samples[:]
    rng.shuffle(shuffled)
    chosen: list[FileSample] = []
    seen_instruments: set[str] = set()
    for sample in shuffled:
        if sample.instrument_dir in seen_instruments:
            continue
        chosen.append(sample)
        seen_instruments.add(sample.instrument_dir)
        if len(chosen) == sample_per_family:
            return sorted(chosen, key=lambda item: (item.instrument_dir, item.path.as_posix()))
    return sorted(shuffled[:sample_per_family], key=lambda item: (item.instrument_dir, item.path.as_posix()))


def _ensure_stanford_mer_example(
    sampled: list[FileSample],
    samples_by_family: dict[str, list[FileSample]],
    rng: random.Random,
) -> list[FileSample]:
    if any(_is_stanford_mer_example(sample) for sample in sampled):
        return sampled
    candidates = [
        sample
        for family in ("mer_event_records", "mer_environment_records", "mer_parameter_records")
        for sample in samples_by_family.get(family, [])
        if _is_stanford_mer_example(sample)
    ]
    if not candidates:
        return sampled
    sampled.append(rng.choice(candidates))
    unique: dict[tuple[str, str], FileSample] = {}
    for sample in sampled:
        unique[(sample.family, sample.path.as_posix())] = sample
    return list(unique.values())


def _is_stanford_mer_example(sample: FileSample) -> bool:
    if not sample.family.startswith("mer_"):
        return False
    if sample.instrument_dir.startswith("465.152-R-"):
        return True
    row = sample.sample_row
    return row.get("raw_format_line") is None and row.get("rounds") is not None


def _check_log_battery_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    match = BATTERY_PATTERN.search(row["raw_line"])
    if match is None:
        return ["raw_line does not contain a parseable battery voltage/current pattern"]
    if int(match.group(1)) != row.get("voltage_mv"):
        issues.append("voltage_mv does not match the preserved raw_line value")
    if int(match.group(2)) != row.get("current_ua"):
        issues.append("current_ua does not match the preserved raw_line value")
    return issues


def _check_log_pressure_temperature_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    match = PRESSURE_TEMPERATURE_PATTERN.search(row["raw_line"])
    if match is None:
        return ["raw_line does not contain a parseable pressure/temperature pattern"]
    if int(match.group(1)) != row.get("pressure_mbar"):
        issues.append("pressure_mbar does not match the preserved raw_line value")
    if int(match.group(2)) != row.get("temperature_mdegc"):
        issues.append("temperature_mdegc does not match the preserved raw_line value")
    return issues


def _check_log_acquisition_row(row: dict[str, Any]) -> list[str]:
    expected = ACQUISITION_MESSAGES.get(row.get("message"))
    if expected is None:
        return ["message is not one of the explicit acquisition evidence forms"]
    issues: list[str] = []
    if row.get("acquisition_state") != expected[0]:
        issues.append("acquisition_state does not match the explicit raw message")
    if row.get("acquisition_evidence_kind") != expected[1]:
        issues.append("acquisition_evidence_kind does not match the explicit raw message")
    return issues


def _check_log_ascent_request_row(row: dict[str, Any]) -> list[str]:
    message = row.get("message", "")
    if "accepted" in message and row.get("ascent_request_state") != "accepted":
        return ["ascent_request_state does not match the explicit raw message"]
    if "rejected" in message and row.get("ascent_request_state") != "rejected":
        return ["ascent_request_state does not match the explicit raw message"]
    return []


def _check_grouped_log_row(row: dict[str, Any]) -> list[str]:
    raw_lines = row.get("raw_lines") or []
    if not raw_lines:
        return ["grouped family row is missing preserved raw_lines"]
    issues: list[str] = []
    if row.get("start_log_epoch_time") and not raw_lines[0].startswith(str(row["start_log_epoch_time"])):
        issues.append("start_log_epoch_time does not match the first preserved raw line")
    if row.get("end_log_epoch_time") and not raw_lines[-1].startswith(str(row["end_log_epoch_time"])):
        issues.append("end_log_epoch_time does not match the last preserved raw line")
    if row.get("line_start_index", 0) > row.get("line_end_index", 0):
        issues.append("line_start_index is greater than line_end_index")
    return issues


def _check_log_transmission_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    referenced_artifact = row.get("referenced_artifact")
    if referenced_artifact is not None:
        if "/" in referenced_artifact:
            issues.append("referenced_artifact is not canonicalized to a basename-style artifact name")
        raw_line = row.get("raw_line", "")
        raw_artifact = referenced_artifact.replace("_", "/", 1)
        if raw_artifact not in raw_line and referenced_artifact not in raw_line:
            issues.append("referenced_artifact cannot be reconciled with the preserved raw_line")
    if row.get("transmission_kind") == "upload_disconnect" and row.get("disconnect_duration_s") is None:
        issues.append("upload_disconnect row is missing disconnect_duration_s")
    return issues


def _check_mer_environment_row(row: dict[str, Any]) -> list[str]:
    raw_values = row.get("raw_values") or {}
    issues: list[str] = []
    if row.get("environment_kind") == "board" and raw_values.get("board") != row.get("board"):
        issues.append("board does not match raw_values['board']")
    if row.get("environment_kind") == "sample":
        if _int_or_none(raw_values.get("min")) != row.get("sample_min"):
            issues.append("sample_min does not match raw_values['min']")
        if _int_or_none(raw_values.get("max")) != row.get("sample_max"):
            issues.append("sample_max does not match raw_values['max']")
    if row.get("environment_kind") == "gpsinfo" and raw_values.get("date") != row.get("gpsinfo_date"):
        issues.append("gpsinfo_date does not match raw_values['date']")
    return issues


def _check_mer_parameter_row(row: dict[str, Any]) -> list[str]:
    raw_values = row.get("raw_values") or {}
    issues: list[str] = []
    if row.get("parameter_kind") == "adc":
        if raw_values.get("buffer") != row.get("adc_buffer"):
            issues.append("adc_buffer does not match raw_values['buffer']")
        if _int_or_none(raw_values.get("gain")) != row.get("adc_gain"):
            issues.append("adc_gain does not match raw_values['gain']")
    return issues


def _check_mer_event_row(row: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    encoded_payload = row.get("encoded_payload")
    if encoded_payload is not None:
        payload_nbytes = len(base64.b64decode(encoded_payload))
        if payload_nbytes != row.get("encoded_payload_byte_count"):
            issues.append("encoded_payload_byte_count does not match the decoded payload size")
        if payload_nbytes != row.get("data_payload_nbytes"):
            issues.append("data_payload_nbytes does not match the decoded payload size")
    raw_info_line = row.get("raw_info_line") or ""
    for field_name, token in (
        ("event_info_date", "DATE"),
        ("pressure", "PRESSURE"),
        ("temperature", "TEMPERATURE"),
        ("criterion", "CRITERION"),
        ("snr", "SNR"),
        ("trig", "TRIG"),
        ("detrig", "DETRIG"),
        ("rounds", "ROUNDS"),
    ):
        value = row.get(field_name)
        if value is not None and f"{token}={value}" not in raw_info_line:
            issues.append(f"{field_name} is not preserved in raw_info_line")
    raw_format_line = row.get("raw_format_line") or ""
    if raw_format_line:
        for field_name, token in (
            ("endianness", "ENDIANNESS"),
            ("bytes_per_sample", "BYTES_PER_SAMPLE"),
            ("sampling_rate", "SAMPLING_RATE"),
            ("stages", "STAGES"),
            ("normalized", "NORMALIZED"),
            ("length", "LENGTH"),
        ):
            value = row.get(field_name)
            if value is not None and f"{token}={value}" not in raw_format_line:
                issues.append(f"{field_name} is not preserved in raw_format_line")
    elif row.get("rounds") is None:
        issues.append("event row is missing both raw_format_line context and Stanford rounds-style INFO data")
    return issues


def _finding_row_detail(row: dict[str, Any]) -> dict[str, Any]:
    detail = {}
    for key in (
        "message",
        "raw_line",
        "line",
        "raw_info_line",
        "raw_format_line",
        "referenced_artifact",
        "pressure_mbar",
        "temperature_mdegc",
        "voltage_mv",
        "current_ua",
    ):
        if key in row and row[key] is not None:
            detail[key] = row[key]
    if "raw_lines" in row:
        detail["raw_lines_preview"] = row["raw_lines"][:4]
        detail["raw_lines_count"] = len(row["raw_lines"])
    return detail


def _confidence_label(findings: list[dict[str, Any]], sample_count: int) -> str:
    if findings:
        return "moderate"
    if sample_count >= 10:
        return "moderate-high"
    return "moderate"


def _format_console_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Records root: {report['records_root']}",
        f"Seed: {report['seed']}",
        f"Sample per family: {report['sample_per_family']}",
        f"Non-empty families: {len(report['inventory'])}",
        "Coverage: "
        + ("all non-empty families sampled" if report["covered_every_nonempty_family"] else "incomplete"),
        f"Touched instruments: {len(report['touched_instruments'])}",
        f"Confidence: {report['confidence']}",
    ]
    if report["findings"]:
        lines.append("Findings:")
        for finding in report["findings"]:
            lines.append(
                f"- {finding['family']} {finding['path']}:{finding['sample_line_num']} "
                + "; ".join(finding["issues"])
            )
    else:
        lines.append("Findings: none from sampled rows")
    return "\n".join(lines)


def _int_or_none(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value)
