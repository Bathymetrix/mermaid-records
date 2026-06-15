# Changelog

## 2.0.0

Breaking output contract changes:

- Added `instrument_serial` to every normalized LOG and MER JSONL record.
- Renamed normalized JSONL family files to `<family>.<instrument_serial>.jsonl`.
- Added `instrument_serial` to relevant manifests and state/diagnostic rows that already carry instrument context.
- Changed stateful run directory IDs to UTC ISO8601-style timestamps such as `2026-04-21T22:17:31Z-11a3ef`.
- Kept raw unmatched LOG rows exclusive to `log_unclassified_records` instead of duplicating them in `log_operational_records`.
