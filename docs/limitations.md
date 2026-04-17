# Limitations

## MER event preservation

MER event records do not preserve the full original `<EVENT>...</EVENT>` block verbatim.

Instead, successful normalized event rows preserve structured components such as:

- `raw_info_line`
- `raw_format_line`
- encoded payload fields

This is sufficient for many downstream uses, but it is not byte-for-byte reconstruction of the full original event block.

## JSONL versus manifests

Normalized JSONL outputs contain valid structured records.

When stateful mode is enabled, malformed or non-normalizable content is also recorded in manifest-side audit outputs. In stateless mode, manifest outputs are not written, so malformed content is not persisted there as a separate artifact.

For this reason, documentation about malformed-content capture should always be read together with the execution mode described in `docs/cli.md`.

## Execution-mode effects

Some output structures and audit behaviors depend on execution mode.

In particular:

- `manifests/` and `state/` are stateful-mode artifacts
- stateless mode does not write manifests
- rewrite and bookkeeping behavior should be interpreted in the context of the selected mode

## Allowed transformations

The following explicit transformations may occur during normalization:

- trailing newline normalization (`\r\n` stripped during line reads)
- artifact path canonicalization (`/` → `_`) where referenced filenames are normalized for stable output
- minimal parsing required to expose structured fields

No additional interpretation-oriented transformations are part of the v1 contract.

## Float and family variability

Not every float emits every record family, and not every family populates every optional field.

Examples include:

- some floats populate `log_parameter_records.jsonl` as an empty file because no parameter episodes were present
- `log_sbe_records.jsonl` may be present but empty depending on float/data generation
- Stanford PSD MER events may be valid but intentionally sparse in scalar fields compared with acoustic MERMAID examples

Such absence or sparsity is data dependent and does not by itself imply a normalization defect.

## External decoder dependency

`BIN` handling depends on an external preprocess/decode step that produces `LOG` artifacts.

`mermaid-records` does not currently replace that decoder. Any operational limitations, environment assumptions, or failure modes associated with the external decoder remain outside the scope of this package's normalization contract.
