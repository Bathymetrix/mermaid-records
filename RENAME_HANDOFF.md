# RENAME HANDOFF

This repo is being prepared for a clean rename only. Do not preserve the old repo path in working assumptions once the filesystem rename is done.

Current repo path:
- `/Users/jdsimon/programs/mermaid-timeline`

Planned new repo path:
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
- discovery: `src/mermaid_timeline/discovery.py`
- decode: `src/mermaid_timeline/bin2log.py`, `src/mermaid_timeline/bin2cycle.py`
- parsing: `src/mermaid_timeline/operational_raw.py`, `src/mermaid_timeline/mer_raw.py`
- LOG normalization prototype: `src/mermaid_timeline/normalize_log.py`
- audit/dev workflows: `src/mermaid_timeline/audit.py`, `scripts/`

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
- `src/mermaid_timeline/cycle_raw.py` remains as a legacy compatibility shim
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

## Exact Rename Targets

Rename these when doing the actual rename:
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

## Rename-Sensitive References To Update

1. `pyproject.toml`
- `[project].name = "mermaid-timeline"`
- `[project.scripts] mermaid-timeline = "mermaid_timeline.cli:main"`
- `[tool.setuptools.dynamic] version = {attr = "mermaid_timeline.__version__"}`

2. Source package directory
- `src/mermaid_timeline/`

3. Imports across repo
- imports under `src/`, `tests/`, and `scripts/` currently use `mermaid_timeline`
- direct import updates are required across:
  - `scripts/`
  - `tests/`
  - package-internal imports if any absolute package imports are introduced later

4. CLI references
- `src/mermaid_timeline/cli.py`
  - module docstring mentions `mermaid_timeline`
  - `argparse.ArgumentParser(prog="mermaid-timeline")`

5. `AGENTS.md`
- contains explicit path references such as:
  - `src/mermaid_timeline/__init__.py`
  - `src/mermaid_timeline/cli.py`
  - `src/mermaid_timeline/operational_raw.py`
  - `src/mermaid_timeline/cycle_raw.py`
- contains package-name text:
  - ``mermaid-timeline``
  - ``mermaid_timeline``

6. `README.md`
- title and prose mention `mermaid-timeline`
- CLI usage examples use `mermaid-timeline`

7. Package metadata/runtime surface
- `src/mermaid_timeline/__init__.py`
  - top-level package docstring mentions `mermaid_timeline`
  - canonical version path will need to move to `src/mermaid_records/__init__.py`

## Things That Should Not Change During Rename

Do not change during the rename unless separately intended:
- LOG JSONL output filenames
- current normalization schemas
- representative fixture filenames
- parser function names unless there is a separate cleanup decision

## After Filesystem Rename, Do These In The New Codex Project

1. Open Codex on:
   - `/Users/jdsimon/programs/mermaid-records`
2. Verify the detected project root is the renamed Git root.
3. Perform the actual package rename:
   - repo/distribution/import package/CLI
4. Reinstall editable package:
   - `./.venv/bin/python -m pip install -e . --no-build-isolation`
5. Run tests:
   - `./.venv/bin/python -m pytest -q`
6. Verify CLI help:
   - `./.venv/bin/python -m mermaid_records.cli --help`
   - and/or installed command help for `mermaid-records`
7. Then begin MER normalization work.

## Practical Notes

- This handoff assumes a new Codex session rooted at the renamed repo path.
- Do not preserve the old filesystem path in new working instructions.
- Do not add a package-rename compatibility shim unless the rename plan changes.
