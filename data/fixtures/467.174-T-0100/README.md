# Fixture Provenance

This fixture family is organized from the canonical artifacts for float `467.174-T-0100`.

- `bin/` contains raw `BIN` files copied from `~/mermaid/server`.
- `log/` contains canonical `LOG` files decoded from `BIN` by automaid `preprocess.py`.
- `mer/` contains raw `MER` files copied from `~/mermaid/server`.
- `s61/` contains canonical `S61` files decoded by automaid.
- `cycle/` contains canonical `CYCLE` files produced by automaid from concatenated `LOG` content.

Source revisions:

- automaid commit: `9a1b27013742f3ebc9f2268684f653a252c6628a`
- server commit: `2ff0dca66a386a66caa64415d666e4baf25401d6`
