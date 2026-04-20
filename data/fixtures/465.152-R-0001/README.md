# Fixture Provenance

This fixture family is organized from a compact raw PSD / Stanford-style subset for float `465.152-R-0001`.

- `bin/` contains paired raw `BIN` files copied from `~/mermaid/server_everyone`.
- `mer/` contains paired raw `MER` files copied from `~/mermaid/server_everyone`.

This release-focused subset intentionally keeps only the smallest paired raw files needed to back real PSD / Stanford-style fixture coverage.

- `0001_6255B101.MER` is a metadata-only Stanford `MER` with zero `<EVENT>` blocks.
- `0001_625CB0C0.MER` is a compact real Stanford `MER` with ten `<EVENT>` blocks and no `<FORMAT>` lines.
- `0001_6255B10B.BIN` and `0001_625CB0DC.BIN` are the paired raw `BIN` artifacts kept with the same subset.

No decoded `log/` or `s61/` branch is included in this pass because the goal here is honest raw PSD fixture coverage, not external decoder coverage.

Source revisions:

- server_everyone commit: `841bad1971fcbf89cba31454f220ff0635289ed3`
