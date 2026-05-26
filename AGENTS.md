# AGENTS

## Persistent Rules

- “prototype” terminology in normalization code/docs refers to earlier development-phase design work; for v1, normalization families and rules are treated as stable.
- Code-level naming should therefore prefer “families” for active normalization entrypoints, while historical references may remain when context matters.

- Never mix parsing and interpretation.
- Keep record interfaces stable.
- Always preserve unknown MER record types.
- Prefer generators for file parsing where practical.
- Add or update tests with any real logic change.
- Prefer small, coherent commits and always tell the user when the current state is a good time to commit.
- Any time suggesting a commit, also suggest a matching commit message.
- Do not suggest `type: message` commit subjects by default; prefer clear, simple, project-specific commit messages.
- Treat this file as the persistent handoff document for future Codex sessions and update it when assumptions, boundaries, fixtures, or workflow rules change.
- Add the exact Bathymetrix header only to `src/mermaid_records/__init__.py` and `src/mermaid_records/cli.py`.
- Do not add the Bathymetrix header to `README.md`, tests, or internal implementation modules unless the user explicitly asks.
- Never delete source raw files from their original path. This includes `.BIN`, `.LOG`, `.MER`, and future raw formats such as `.vit`. If an external decoder is destructive, it must run only on copied files in a temporary workspace.
- Before writing a new audit workflow, first scan existing audit code for reusable logic and easy refactors instead of starting from a fresh script by default.
- Keep code DRY, but verify behavior before and after any DRY-driven refactor instead of assuming equivalence.
- Always push back, disagree, or suggest a better alternative when warranted.
- Package license defaults to MIT. A root `LICENSE` file must exist.
- Every Python source file must include `SPDX-License-Identifier: MIT`, but must not include the full license text.
- Prefer clear, simple Pythonic comments, and start comment text with a capital letter.
- Use `Bathymetrix™` only in approved file headers and rare top-level visible branding. Do not use the trademark marker in identifiers, module names, imports, docstrings, or inline comments.
- Package authorship/licensing metadata must live in exactly one location: `src/mermaid_records/__init__.py` via `__author__`, `__license__`, and `__copyright__`.
- `CYCLE` / `CYCLE.h` are out of scope for `mermaid-records` and must not be reintroduced unless the user explicitly requests it.

## Versioning Rule

- The canonical version must live in `src/mermaid_records/__init__.py` as `__version__`.
- `pyproject.toml` must use dynamic versioning via `[tool.setuptools.dynamic]` with `version = {attr = "mermaid_records.__version__"}`.
- No other hardcoded package version strings are allowed in the repo.
- Until the release is finalized, use release-candidate versions such as `2.0.0-rc1` and bump the `rc` suffix sequentially (`rc2`, `rc3`, etc.) for each candidate.
- The package-root Python surface for v1 is intentionally minimal metadata only; do not re-export broader functional helpers from `mermaid_records.__init__` unless the user explicitly expands the supported API.

## Namespace Consolidation / Public API Discipline

AGENTS should keep future namespace consolidation in mind during all implementation and API decisions.

This project may eventually become part of a larger unified namespace layout such as:

    src/mermaid_records/   -> src/mermaid/records/
    src/mermaid_timeline/  -> src/mermaid/timeline/
    src/mermaid_telemetry/ -> src/mermaid/telemetry/
    src/mermaid_gcmt/      -> src/mermaid/gcmt/

Therefore:

- prioritize stable CLI/file-format contracts over stable internal import paths
- keep public Python API exposure intentionally small
- avoid exposing internal helpers/classes/functions unless clearly intended as durable public API
- avoid documenting deep import paths as stable interfaces
- prefer CLI-driven workflows over broad import-driven workflows

Key philosophy:

- The primary public contract is:
  - CLI behavior
  - documented file formats/schemas
  - manifests/state behavior
  - documented validation behavior
- Internal Python module layout is NOT yet considered stable public API.

Guidelines:

- Avoid unnecessary re-exports in `__init__.py`.
- Internal modules/functions/classes may be reorganized freely unless explicitly documented as public API.
- Prefer stable CLI entry points and stable JSONL/file contracts over stable internal module paths.
- Use centralized constants/helpers for package metadata where practical (package name, schema version, filenames, etc.) rather than scattering hardcoded package names throughout the codebase.
- Do not over-engineer namespace-package machinery prematurely; just avoid choices that would make later migration painful.
- Before exposing/importing/re-exporting new symbols publicly, consider whether doing so creates a long-term compatibility obligation.
- When introducing new public APIs, consider whether they would remain sensible after a future migration from:

      mermaid_<thing>

  to:

      mermaid.<thing>

Tests may import internal modules freely; test imports are not considered stable public API.

## Project Purpose

`mermaid-records` is a Python package to normalize `BIN`, `LOG`, and `MER` into parseable record families.

Supported inputs currently include:

- `.BIN` files
- `.LOG` files
- `.MER` files

This layer is strictly for parsing and structured extraction.

Do not add:

- unit conversions
- coordinate conversions
- inferred durations from sample counts and rates
- acquisition inference beyond explicit `acq started` / `acq stopped`
- DET / REQ logic
- higher-level timeline interpretation
- workflow-engine behavior beyond the normalization pipeline

## Current Parsing Scope

Canonical source model:

- upstream raw `.BIN`
- upstream raw `.LOG`
- upstream raw `.MER`

Decode/parsing boundary:

- decode: raw `BIN` -> decoded `LOG`
- parsing: consume raw `LOG` and raw `MER`
- interpretation/timeline logic remains separate and should not be mixed into either layer

For v1 normalization work, the canonical decode seam is `BIN` -> `LOG`.

Mirror the upstream preprocess call order responsibly:

- `database_update(...)` is a batch preflight step
- `concatenate_files(...)` and `decrypt_all(...)` are part of the per-workspace `BIN` -> `LOG` decode path
- `concatenate_rbr_files(...)` may also be part of preprocessing, but should not force interpretation into the decode layer

Do not call `database_update(...)` once per `BIN`; prefer a single explicit refresh before a batch decode workflow.
Preflight policy is mode-dependent:

- `strict`: fail closed
- `cached`: allow explicit degraded continuation when live refresh fails, and record/report that degraded preflight state clearly

### Operational Text Sources

Use one common `OperationalLogEntry` model for `LOG` with:

- `time`
- `subsystem`
- `code`
- `message`
- `source_kind`
- `raw_line`
- `source_file`

Preserve source identity via `source_kind = "log"`.

Normalized record-family direction to keep in mind during cleanup and naming:

- `operational_records`
- `location_records`
- `transmission_records`
- `acquisition_records`
- `ascent_request_records`
- `parameter_records`
- `testmode_records`
- `sbe_records`
- `mer_event_blocks`
- `acquisition_intervals`
- `pressure_temperature_records`
- `battery_records`
- `gps_records`
- `unclassified_operational_records`

For LOG-derived measurement-adjacent lines:

- dedicated `log_pressure_temperature_records` output family is only for literal `P...mbar,T...mdegC` observations with parsed `pressure_mbar` and `temperature_mdegc`
- dedicated `log_battery_records` output family is only for literal `battery ...mV, ...uA` telemetry with parsed `voltage_mv` and `current_ua`
- other lines that were formerly routed into `log_measurement_records` now remain only in `log_operational_records`; do not expand their parsing without an explicit request

For normalized LOG/MER family boundaries:

- split files by coherent subsystem or workflow, not by the presence of a primary scalar field
- keep structurally different line kinds together when they describe one process or state machine, using internal `*_kind` fields instead of fragmenting them into one-file-per-scalar outputs
- avoid reviving vague mixed-domain buckets like the former measurement family

For derived operational-family prototypes, no parsed `OperationalLogEntry` should disappear silently. Each parsed operational line must end up either in exactly one derived family stream or in `unclassified_operational_records`.

Operational-family routing contract:

- grouped structural LOG routes such as `parameter`, `testmode`, and `sbe` are resolved before ordinary `OperationalLogEntry` family classification
- every ordinary `OperationalLogEntry` always emits one record to the `log_operational_records` family
- after that, an ordinary operational line may match zero or one derived family
- zero derived matches route to the `log_unclassified_records` family
- two or more derived matches are a normalization bug and must fail loudly; do not hide them with precedence or multi-family emission

For acquisition evidence prototypes, preserve the distinction between exact transitions and state assertions:

- `acq started` / `acq stopped` are transition evidence
- `acq already started` / `acq already stopped` are assertion evidence

Do not infer intervals from assertion lines in the normalization layer.

For ascent-request prototypes, classify only explicit request outcomes such as `ascent request accepted` and `ascent request rejected`. Do not infer ascent-request state from other ascent-related lines.

For GPS prototypes, emit one record per clearly GPS-related LOG line such as `GPS fix...`, raw latitude/longitude lines, `hdop`/`vdop`, `GPSACK`, and `GPSOFF`. Do not group lines into fixes or compute derived position/timing values in the normalization layer.

For rollover banner lines like `timestamp:*** switching to 0026/5D4A3E75 ***`, preserve them as operational LOG records instead of malformed lines and emit `switched_to_log_file` with canonical filename normalization.

Whenever LOG content is parsed as a LOG or MER filename reference, canonicalize only that parsed filename by replacing `/` with `_`. If the context implies a LOG rollover target, emit the canonical `.LOG` filename form.

For generated JSONL filenames, prefix LOG-derived outputs with `log_` and reserve analogous `mer_` prefixes for MER-derived outputs.

Acquisition windows may be extracted only from explicit:

- `acq started`
- `acq stopped`

Ignore lines like:

- `acq already started`
- `acq already stopped`

### `.MER`

Parse `.MER` files into:

- one `MerFileMetadata`
- zero or more `MerEventBlock` values

For metadata:

- preserve raw `ENVIRONMENT` lines
- preserve raw `PARAMETERS` lines
- extract repeated `GPSINFO`, `DRIFT`, and `CLOCK` structures conservatively
- keep GPS coordinates in raw string form
- valid Stanford PSD `.MER` files may contain `<ENVIRONMENT>` + `<PARAMETERS>` and zero `<EVENT>` blocks; normalize these cleanly without treating them as malformed

For event blocks:

- parse `INFO`
- parse `FORMAT` when present, but allow valid Stanford PSD event blocks that contain `INFO` + `DATA` without `FORMAT`
- preserve `DATA` payload bytes without waveform interpretation
- for payload byte counts, measure only the bytes strictly inside `<DATA> ... </DATA>` and exclude surrounding framing bytes such as `\n`, `\r`, and `\t`

## Current File/Layout Assumptions

- The primary shared LOG parser module is `src/mermaid_records/parse_log.py`.
- Discovery should cover only raw `BIN`, `LOG`, and `MER` inputs relevant to this package.
- `LOG` is the native per-dive operational source.
- A single `.MER` may include DET data from the current dive plus REG/REQ data from previous dives. Do not infer dive membership from `MerEventBlock.date` during parsing.
- The normalize CLI matrix audit helper lives in `src/mermaid_records/_audit_normalize_cli.py` with the repo script wrapper at `scripts/audit_normalize_cli_matrix.py`.
- The normalized-output randomized audit helper lives in `src/mermaid_records/_audit_normalized_outputs.py` with the repo script wrapper at `scripts/audit_normalized_outputs.py`.
- The normalize CLI matrix audit defaults to a semantic flag matrix; exhaustive boolean expansion is opt-in.

## Current Fixtures

Tracked fixtures currently include:

- `data/fixtures/452.020-P-06/log/*.LOG`
- `data/fixtures/452.020-P-06/mer/*.MER`
- `data/fixtures/452.020-P-06/README.md`
- `data/fixtures/465.152-R-0001/bin/*.BIN`
- `data/fixtures/465.152-R-0001/mer/*.MER`
- `data/fixtures/465.152-R-0001/README.md`
- `data/fixtures/467.174-T-0100/bin/*.BIN`
- `data/fixtures/467.174-T-0100/log/*.LOG`
- `data/fixtures/467.174-T-0100/mer/*.MER`
- `data/fixtures/467.174-T-0100/s61/*.S61`
- `data/fixtures/467.174-T-0100/README.md`

The representative JSONL prototype fixture sets under `data/fixtures/log_examples_representative_06_0100/` and `data/fixtures/mer_examples_representative_06_0100/` remain in scope for inspection.

The compact PSD Stanford-style fixture family under `data/fixtures/465.152-R-0001/` intentionally tracks paired raw `BIN` + `MER` artifacts only. Do not invent or require a decoded `log/` branch for that family unless the user explicitly asks for decoder-backed PSD fixtures.

## Workflow Rules

- If work shifts toward higher-level API design, abstraction tradeoffs, naming strategy, or broader architecture, say when it may be a good moment to consult ChatGPT and provide a concise handoff summary.
- Do not be territorial about tool choice; suggest ChatGPT when it is likely to help with design-space exploration.
- When CI status matters, check GitHub Actions with GitHub CLI before relying only on local verification: if `gh` is available, run `gh run list --limit 5` to identify the relevant recent workflow run, then inspect it with `gh run view <run-id> --json status,conclusion,jobs` or equivalent. Report the workflow conclusion and each relevant matrix job conclusion, especially Python-version matrix entries. If `gh` is unavailable or unauthenticated, say so clearly and fall back to local verification. Do not make git-mutating commands unless explicitly asked.
- The normalize CLI matrix audit workflow should isolate each run in its own output sandbox, capture `stdout`/`stderr` per run, append one JSONL result row per attempt, and keep going after failures.
- For BIN-backed audit runs, preserve a real decoder `MERMAID` root for automaid while keeping output-resolution tests sandboxed by seeding only the isolated audit root `database/` link when needed.

## Module Naming Rule

All transformation and processing modules should use action-first naming.

Examples:

- `normalize_log.py`
- `normalize_mer.py`
- `parse_log.py`
- `parse_mer.py`

Avoid:

- `log_normalize.py`
- `mer_normalize.py`

## Normalization Guardrails

- Always preserve the original source representation.
- Always include the raw source line or block where applicable.
- Do not drop, merge, or reinterpret source records silently.
- Prefer source-literal field names when they exist.
- One JSONL record should correspond to one real source unit.
- Normalize structure, not meaning.
- Except for explicitly preserved raw source strings such as `raw_line`, `raw_lines`, `line`, `raw_info_line`, `raw_format_line`, and `raw_values`, all emitted date/time strings must use UTC ISO8601 with six fractional digits and a `Z` suffix, for example `2020-12-14T05:22:31.000000Z`. Convert timezone-aware inputs to UTC before formatting; do not simply append `Z`.

## Current Pipeline Rules

- The normalization pipeline has two execution modes:
  - `stateful`: directory input, manifests enabled, incremental rerun logic enabled
  - `stateless`: explicit file-list input, no manifests, no incremental logic, no pruning
- Stateless reruns are rewrite-only for targeted instrument outputs; never append in stateless mode, even when the explicit inputs are unchanged.
- Stateless mode must error if the target output directory already contains manifests.
- Stateful incremental behavior is binary and conservative:
  - append only when the only change is newly added raw source files
  - rewrite when any previously seen raw source changes or is removed
  - decoder-state changes invalidate only BIN-derived outputs for BIN-dependent floats
  - explicit force-rewrite mode may override incremental append/noop decisions and force targeted family rewrites
- JSONL outputs use deterministic processing order, not time-order.
- Normalized JSONL outputs should use basename-only `source_file`; richer full-path provenance belongs in manifests and other run-side artifacts.
- Do not mutate existing JSONL outputs in place; append and full rewrite are the only safe modification paths.
- `--force-rewrite` must remove package-owned generated artifacts for each targeted instrument before regeneration: all top-level `log_*.jsonl`, all top-level `mer_*.jsonl`, and package-owned bookkeeping under `manifests/` and `state/`. Do not delete unknown files or the whole instrument directory.
- `preflight_status.json` is run-scoped bookkeeping: clear stale root artifacts before each real run, and include `preflight_status` in `manifests/latest.json` only when the current run produced that artifact. When no preflight runs, omit the field rather than storing `null`.
- Every per-instrument output directory must materialize the canonical serial-suffixed output file set even when some families are empty. At minimum this means all top-level LOG and MER JSONL family files named `<family>.<instrument_serial>.jsonl` must exist as empty files when they have no records; in `stateful` mode also keep the state/manifest scaffold present for that instrument, while `stateless` mode still must not create manifests.
- Future dry-run/report behavior must be completely side-effect free, including no file writes of any kind.
- Persisted `manifests/runs/<run_id>/input_file_diffs.jsonl` is a strict raw input diff log: file-level fields only, no append/rewrite/noop semantics, and no standalone non-file invalidation records.
- Canonical `instrument_id` should be parsed from the Osean serial naming rules when a full serial is available, for example `452.020-P-08 -> P0008` and `467.174-T-0100 -> T0100`. Do not derive canonical `instrument_id` independently in multiple modules.
- Stateful manifest run directories use UTC ISO8601-style IDs with separators, for example `manifests/runs/2026-04-21T22:17:31Z-11a3ef/`.

## Instrument Terminology

- Refer to full names such as `467.174-T-0100` as the **instrument serial**.
- Refer to canonical 5-character station names such as `T0100` as the  **instrument ID**.
- Keep `instrument_id` and `instrument_serial` distinct in normalized records, filenames, manifests, state/diagnostic records that already carry instrument context, schema/docs, tests, diagnostics, commit messages, and user-facing explanations.
- `instrument_id` remains the station/instrument identifier analogous to `kstnm`; `instrument_serial` is the full hardware/dataset serial such as `452.020-P-06`.
- If stateless `--input-file` context cannot resolve a full serial from nearby path/log context, the current contract falls back to the raw file prefix for `instrument_serial`; document that ambiguity rather than inventing a broader CLI/API surface.
