# SPDX-License-Identifier: MIT

"""External adapter layer for upstream BIN-to-LOG decoding."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Iterator


@dataclass(slots=True)
class Bin2LogConfig:
    """Configuration for invoking the external manufacturer decoder."""

    python_executable: Path
    decoder_script: Path


class Bin2LogError(RuntimeError):
    """Raised when external BIN-to-LOG decoding fails."""


def iter_decoded_log_lines(path: Path, *, config: Bin2LogConfig) -> Iterator[str]:
    """Yield decoded LOG text lines for one raw .BIN file.

    Observed manufacturer decoder I/O contract:

    - `preprocess.py` decodes `.BIN` files into `.LOG` files via `decrypt_all(...)`
    - the later `convert_in_cycle(...)` step derives `CYCLE` files from decoded LOGs
    - the manufacturer workflow may delete the working-copy `.BIN`

    The adapter therefore:

    - copies the requested `.BIN` into a temporary working directory
    - invokes only the LOG decode step in a subprocess
    - reads emitted `.LOG` artifact(s)
    - leaves the original source `.BIN` untouched
    """

    _validate_inputs(path, config)

    with _decoded_log_workspace(path, config) as workdir:
        log_paths = sorted(workdir.glob("*.LOG"))
        if not log_paths:
            raise Bin2LogError(
                f"External decoder did not emit any .LOG files for {path}."
            )

        for log_path in log_paths:
            with log_path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    yield raw_line.rstrip("\r\n")


def _validate_inputs(path: Path, config: Bin2LogConfig) -> None:
    """Validate adapter inputs before subprocess invocation."""

    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_file():
        raise Bin2LogError(f"BIN input is not a file: {path}")
    if not config.python_executable.exists():
        raise FileNotFoundError(config.python_executable)
    if not config.decoder_script.exists():
        raise FileNotFoundError(config.decoder_script)


class _DecodedLogWorkspace:
    """Context manager for a temporary BIN->LOG decode workspace."""

    def __init__(self, path: Path, config: Bin2LogConfig) -> None:
        self._path = path
        self._config = config
        self._tmpdir: tempfile.TemporaryDirectory[str] | None = None
        self.workdir: Path | None = None

    def __enter__(self) -> Path:
        self._tmpdir = tempfile.TemporaryDirectory(prefix="mermaid-bin2log-")
        self.workdir = Path(self._tmpdir.name)
        bin_copy = self.workdir / self._path.name
        shutil.copy2(self._path, bin_copy)
        _run_log_decoder(self.workdir, self._config)
        return self.workdir

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._tmpdir is not None:
            self._tmpdir.cleanup()


def _decoded_log_workspace(path: Path, config: Bin2LogConfig) -> _DecodedLogWorkspace:
    """Create a temporary workspace containing manufacturer-decoded LOG files."""

    return _DecodedLogWorkspace(path, config)


def _run_log_decoder(workdir: Path, config: Bin2LogConfig) -> None:
    """Invoke the external decoder script for the BIN->LOG step only."""

    harness = """
from pathlib import Path
import os
import runpy
import sys

decoder_script = Path(sys.argv[1]).resolve()
workdir = Path(sys.argv[2]).resolve()

sys.path.insert(0, str(decoder_script.parent))
namespace = runpy.run_path(str(decoder_script))

decrypt_all = namespace["decrypt_all"]

workdir_str = str(workdir) + os.sep
decrypt_all(workdir_str)
"""
    result = subprocess.run(
        [
            str(config.python_executable),
            "-c",
            harness,
            str(config.decoder_script),
            str(workdir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"exit code {result.returncode}"
        raise Bin2LogError(f"External decoder failed: {detail}")
