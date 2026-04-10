# RENAME HANDOFF

This rename handoff has been completed. Treat the new repo/package names below as canonical, and do not preserve the old repo path in working assumptions.

Previous repo path:
- `/Users/jdsimon/programs/mermaid-timeline`

Current repo path:
- `/Users/jdsimon/programs/mermaid-records`

## Current Architecture

Purpose:
- normalize primitive/source MERMAID artifacts into parseable record families
- keep decode, parsing, normalization, audit, and later interpretation separate

Current primitive/source inputs:
- `BIN`
- `LOG`
- `MER`

Derived/reference artifacts still supported:
- emitted `CYCLE`
- processed `.CYCLE.h`
- processed `.MER.env`

Current key layers:
- discovery: `src/mermaid_records/discovery.py`
- decode: `src/mermaid_records/bin2log.py`, `src/mermaid_records/bin2cycle.py`
- parsing: `src/mermaid_records/operational_raw.py`, `src/mermaid_records/mer_raw.py`
- LOG normalization prototype: `src/mermaid_records/normalize_log.py`
- audit/dev workflows: `src/mermaid_records/audit.py`, `scripts/`

## Current LOG JSONL Outputs

Current settled LOG-side generated filenames:
- `log_operational_records.jsonl`
- `log_acquisition_records.jsonl`
- `log_ascent_request_records.jsonl`
- `log_gps_records.jsonl`
- `log_transmission_records.jsonl`
- `log_measurement_records.jsonl`
- `log_unclassified_records.jsonl`

Representative generated examples currently live under:
- `data/fixtures/log_examples_representative_06_0100/jsonl_prototype/`

## Current Naming Decisions

Keep these conceptual decisions:
- `LOG`, `BIN`, and `MER` are primitive/source-facing concepts
- `CYCLE` and `.CYCLE.h` are derived/reference products
- shared parser surfaces should prefer `operational` naming
- transformation modules now prefer action-first naming
- LOG normalization module is `normalize_log.py`

## Current Compatibility Shims

Still present on purpose:
- `src/mermaid_records/cycle_raw.py` remains as a legacy compatibility shim
- `CycleLogEntry = OperationalLogEntry`
- `iter_cycle_events(...)`
- `iter_cycle_files(...)`
- `audit_processed_cycle(...)`

Do not add new rename compatibility layers for the package rename. The planned rename is intended as a clean break.

## Implemented vs Not Yet Implemented

Implemented:
- `BIN -> LOG` external decode adapter
- `BIN -> CYCLE` wrapper path
- shared parsing for `LOG`, `CYCLE`, `.CYCLE.h`
- conservative `.MER` parsing
- LOG-derived JSONL prototype families:
  - operational
  - acquisition
  - ascent request
  - gps
  - transmission
  - measurement
  - unclassified
- representative LOG and MER subsets in `data/fixtures/`

Not yet implemented:
- MER-derived JSONL normalization
- cross-source reconciliation
- DET/REQ interpretation
- timeline inference
- final request-generation/API/product layers

Post-rename next step:
- begin MER normalization work

## Rename Result

Completed rename targets:
- repo dir:
  - `mermaid-timeline` -> `mermaid-records`
- src package dir:
  - `src/mermaid_timeline` -> `src/mermaid_records`
- distribution/project name:
  - `mermaid-timeline` -> `mermaid-records`
- import package:
  - `mermaid_timeline` -> `mermaid_records`
- CLI command:
  - `mermaid-timeline` -> `mermaid-records`

Updated rename-sensitive surfaces:
- `pyproject.toml`
  - `[project].name = "mermaid-records"`
  - `[project.scripts] mermaid-records = "mermaid_records.cli:main"`
  - `[tool.setuptools.dynamic] version = {attr = "mermaid_records.__version__"}`
- source package directory now lives at `src/mermaid_records/`
- imports under `src/`, `tests/`, and `scripts/` now use `mermaid_records`
- `src/mermaid_records/cli.py`
  - module docstring now mentions `mermaid_records`
  - `argparse.ArgumentParser(prog="mermaid-records")`
- `AGENTS.md`
  - package-path references updated to `src/mermaid_records/...`
- `README.md`
  - title and CLI usage examples now use `mermaid-records`
- `src/mermaid_records/__init__.py`
  - top-level package docstring now mentions `mermaid_records`
  - canonical version path now lives at `src/mermaid_records/__init__.py`

## Things That Should Not Change During Rename

Do not change during the rename unless separately intended:
- LOG JSONL output filenames
- current normalization schemas
- representative fixture filenames
- parser function names unless there is a separate cleanup decision

## Validation Completed

Completed verification steps in the renamed repo:
1. Confirmed project root is `/Users/jdsimon/programs/mermaid-records`.
2. Reinstalled the editable package:
   - `./.venv/bin/python -m pip install -e . --no-build-isolation`
3. Ran tests:
   - `./.venv/bin/python -m pytest -q`
4. Verified CLI help:
   - `./.venv/bin/python -m mermaid_records.cli --help`
   - `./.venv/bin/mermaid-records --help`
5. Next planned work remains:
   - begin MER normalization work

## Practical Notes

- This handoff assumes a new Codex session rooted at the renamed repo path.
- Do not preserve the old filesystem path in new working instructions.
- Do not add a package-rename compatibility shim unless the rename plan changes.
