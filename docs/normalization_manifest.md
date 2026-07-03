# SPDX-License-Identifier: MIT

# Normalization Manifest

Every successful non-dry-run normalization writes
`normalization_manifest.json` at the normalized output root. The manifest
content-addresses the complete normalized JSONL corpus currently present
under that root, across all instrument directories.

Stateful run bookkeeping under instrument `manifests/` and `state/`
directories is not normalized corpus data and is not inventoried.
`preflight_status.json` and `normalization_manifest.json` are also excluded.

## Schema

The manifest is a UTF-8 JSON object with these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | Manifest schema version; currently `1`. |
| `mermaid_records_version` | string | Canonical package version that generated the manifest. |
| `git_commit` | string or null | Source repository commit when a Git checkout is available. |
| `git_dirty` | boolean or null | Whether that checkout had tracked or untracked changes; null when unavailable. |
| `generation_command` | string or null | CLI spelling when invoked through the CLI; null for callers that do not provide it. |
| `generated_at` | string | UTC generation time in ISO 8601 form with six fractional digits and `Z`. |
| `input_root` | string or null | Stateful input root as supplied to the pipeline; null for stateless explicit-file runs. |
| `checksum_algorithm` | string | `sha256`. |
| `snapshot_id` | string | Corpus digest as `sha256:<lowercase hexadecimal digest>`. |
| `file_count` | integer | Number of entries in `files`. |
| `files` | array | Normalized file inventory, sorted by `path`. |

Each `files` entry has:

| Field | Type | Meaning |
| --- | --- | --- |
| `path` | string | POSIX-style path relative to the normalized output root. |
| `byte_size` | integer | Raw file size in bytes. |
| `sha256` | string | SHA-256 of the raw file bytes as lowercase hexadecimal. |

The Git, command, timestamp, input-root, and package-version fields are useful
provenance but do not participate in `snapshot_id`.

## Snapshot Digest Algorithm

An independent verifier can reproduce `snapshot_id` exactly:

1. Recursively inventory normalized `*.jsonl` files, excluding files below
   directories named `manifests` or `state`.
2. For every file, compute its relative POSIX path, raw byte size, and SHA-256
   of its raw bytes.
3. Sort entries in ascending relative-path order.
4. For every sorted entry, encode this exact text as UTF-8:

   ```text
   relative_path<TAB>byte_size<TAB>file_sha256<LF>
   ```

   `<TAB>` is one byte `0x09`; `<LF>` is one byte `0x0a`. `byte_size` is
   base-10 ASCII without padding, and `file_sha256` is the 64-character
   lowercase hexadecimal digest.
5. Concatenate those encoded lines without any additional framing and
   SHA-256 hash the resulting bytes.
6. Prefix the lowercase hexadecimal digest with `sha256:`.

The empty corpus therefore has the SHA-256 digest of the empty byte string.
Absolute paths, modification times, traversal order, generation metadata,
command spelling, and the manifest's own bytes never enter this recipe.

## Example

```json
{
  "checksum_algorithm": "sha256",
  "file_count": 2,
  "files": [
    {
      "byte_size": 421,
      "path": "452.020-P-06/log_gps_records.452.020-P-06.jsonl",
      "sha256": "83135e4a33c6472a5c93255b9dc09c9f4ec06e3f970f523b723c60c4c042ecdb"
    },
    {
      "byte_size": 0,
      "path": "452.020-P-06/mer_event_records.452.020-P-06.jsonl",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
  ],
  "generated_at": "2026-07-02T17:30:00.000000Z",
  "generation_command": "mermaid-records normalize -i inputs -o records",
  "git_commit": "0123456789abcdef0123456789abcdef01234567",
  "git_dirty": false,
  "input_root": "inputs",
  "mermaid_records_version": "2.1.0-rc1",
  "schema_version": 1,
  "snapshot_id": "sha256:345780c93bb2b95ca143e477151ae6630de71bb96715692a4fd9501828b7bc63"
}
```
