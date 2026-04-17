# CLI

## Entry point

The installed command is:

```bash
mermaid-records normalize
```

The normalize subcommand does **not** use positional `<input> <output>` arguments.

## Inputs and outputs

Normalization is driven through explicit flags.

Typical forms are:

```bash
mermaid-records normalize --input-root <INPUT_ROOT> --output-dir <OUTPUT_DIR>
```

or, for targeted runs:

```bash
mermaid-records normalize --input-file <INPUT_FILE> --output-dir <OUTPUT_DIR>
```

Depending on the runtime environment, output resolution may also use established environment configuration, but the documented interface should be treated as the flag-based form above.

## Execution modes

The CLI has two important behavioral modes:

- **stateful mode** — writes normalization bookkeeping and manifests
- **stateless mode** — performs normalization without manifest persistence

This distinction matters for:

- whether `manifests/` and `state/` exist
- whether malformed/non-normalizable content is persisted in manifest artifacts
- how rewrite/bookkeeping behavior should be interpreted

If you are documenting or debugging normalization results, always keep the selected execution mode in mind.

## Output families

Typical per-instrument outputs include LOG and MER JSONL families such as:

- `log_acquisition_records.jsonl`
- `log_ascent_request_records.jsonl`
- `log_battery_records.jsonl`
- `log_gps_records.jsonl`
- `log_operational_records.jsonl`
- `log_parameter_records.jsonl`
- `log_pressure_temperature_records.jsonl`
- `log_sbe_records.jsonl`
- `log_testmode_records.jsonl`
- `log_transmission_records.jsonl`
- `log_unclassified_records.jsonl`
- `mer_environment_records.jsonl`
- `mer_event_records.jsonl`
- `mer_parameter_records.jsonl`

Stateful runs may also create:

- `manifests/`
- `state/`

## Force rewrite

`--force-rewrite` is a targeted regeneration mechanism.

For the targeted instrument output directories, it removes package-owned generated artifacts before regeneration so that stale outputs from older layouts do not persist. It should be understood as instrument-scoped cleanup and rebuild, not global deletion of all outputs under the entire output root.

## Operational guidance

For authoritative behavioral details, including mode semantics and contract-level guarantees, pair this document with:

- `docs/limitations.md`
- `docs/notes/normalization_release_contract.md`
