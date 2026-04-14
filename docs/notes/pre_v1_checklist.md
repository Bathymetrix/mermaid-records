# SPDX-License-Identifier: MIT

# Pre-v1.0.0 Checklist

This is the final hardening checklist before `v1.0.0`.
Check items off only when they are truly complete.
The goal is correctness, stability, and release clarity, not feature expansion.

## Public Contract Freeze

- [ ] Explicitly confirm the installed CLI surface for `mermaid-records normalize`
- [ ] Explicitly confirm the stateful vs stateless mode contract
- [ ] Explicitly confirm the BIN decode preflight policy contract (`strict` vs `cached`, default behavior, and persistent `preflight_status.json` semantics)
- [ ] Explicitly confirm the output directory layout contract
- [ ] Explicitly confirm all JSONL output filenames
- [ ] Explicitly confirm all JSONL record-family schemas
- [ ] Explicitly confirm that JSONL outputs are source-ordered and not time-sorted
- [ ] Explicitly confirm the manifest layout contract
- [ ] Explicitly confirm the canonical `float_id` formatting/output contract
- [ ] Record any intentionally unsupported behaviors so they do not drift back in

## Schema Audit

- [ ] Audit long-term stability of all LOG JSONL outputs
- [ ] Audit long-term stability of all MER JSONL outputs
- [ ] Audit `input_file_diffs.jsonl`
- [ ] Audit `pruned_records.jsonl`
- [ ] Confirm `pruned_records.jsonl` semantics are documented clearly (`removed_at` is detection time, not filesystem deletion time)
- [ ] Audit `run.json`
- [ ] Audit `outputs.json`
- [ ] Audit `source_state.json`
- [ ] Audit `preflight_status.json`
- [ ] Confirm that all persisted schemas are documented at the level needed for release

## Incremental And Rerun Correctness

- [ ] Validate first stateful run into an empty output directory
- [ ] Validate second stateful run with no raw-source changes
- [ ] Validate append-only case with newly added LOG inputs
- [ ] Validate append-only case with newly added MER inputs
- [ ] Validate rewrite behavior for changed LOG input
- [ ] Validate rewrite behavior for changed MER input
- [ ] Validate rewrite and prune behavior for removed LOG input
- [ ] Validate rewrite and prune behavior for removed MER input
- [ ] Validate BIN decoder-state invalidation behavior
- [ ] Validate stateless mode into a clean output directory
- [ ] Validate stateless mode into an output directory containing manifests and confirm error behavior
- [ ] Validate stateless mode with `--dry-run` and confirm it produces no manifests, no state files, and no output updates
- [ ] Validate dry-run has zero filesystem side effects
- [ ] Validate dry-run human-readable output
- [ ] Validate dry-run JSON output
- [ ] Validate first-run diff semantics treat prior state as empty (`previous_exists = false`, `previous_size_bytes = 0`, `previous_hash = null`)

## Packaging And Release Readiness

- [ ] Sanity-check `pyproject.toml`
- [ ] Sanity-check versioning and dynamic version source
- [ ] Confirm README install and usage instructions are accurate
- [ ] Confirm CLI help text is accurate and release-ready
- [ ] Confirm root `LICENSE` file is present and correct
- [ ] Confirm SPDX headers and package metadata remain consistent
- [ ] Remove or update stale docs referencing removed behavior or old scope
- [ ] Confirm publish/release metadata is ready for `v1.0.0`

## Final Streamlining Pass

- [ ] Remove dead or legacy internal clutter that should not ship into `v1.0.0`
- [ ] Confirm no unnecessary modules remain in the package
- [ ] Confirm no stale tests remain that preserve superseded behavior
- [ ] Confirm no stale helper scripts remain that imply out-of-scope workflows
- [ ] Confirm the package scope remains tightly limited to normalization only

## Must-Not-Forget

- [ ] Rerun detection still considers both raw input diffs and decoder-state diffs
- [ ] BIN-derived outputs are invalidated when decoder state changes
- [ ] Raw server artifacts are still copied before processing because the external decoder may be destructive
- [ ] Manifest/hash-based rerun logic remains in place for safe operation
