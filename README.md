# mermaid-timeline

`mermaid-timeline` is a small Python package scaffold for low-level MER data ingestion and future timeline interpretation.

The package intentionally separates parsing from interpretation:

- raw `.MER` parsing lives in `mer_raw.py`
- `.LOG` parsing lives in `mer_log.py`
- higher-level interpretation modules stay separate

## Installation

```bash
pip install -e .[dev]
```

## CLI

Inspect a MER file:

```bash
mermaid-timeline inspect-mer /path/to/file.MER
```

Inspect a LOG file:

```bash
mermaid-timeline inspect-log /path/to/file.LOG
```

Both commands currently expose conservative parser stubs intended to preserve raw information without overcommitting to a specific decode format.
