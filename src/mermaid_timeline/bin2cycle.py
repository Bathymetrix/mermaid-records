# SPDX-License-Identifier: MIT

"""External adapter layer for upstream BIN-to-CYCLE decoding."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Iterator

from .bin2log import (
    Bin2LogConfig,
    Bin2LogError,
    _validate_inputs,
    decode_workspace_logs,
    prepare_decode_workspace,
)

Bin2CycleConfig = Bin2LogConfig


class Bin2CycleError(RuntimeError):
    """Raised when external BIN-to-CYCLE decoding fails."""


def iter_decoded_cycle_lines(path: Path, *, config: Bin2CycleConfig) -> Iterator[str]:
    """Yield decoded CYCLE text lines for one raw .BIN file.

    The manufacturer flow is naturally two-stage:

    - `decrypt_all(...)` decodes `.BIN` into intermediate `.LOG`
    - `convert_in_cycle(...)` groups decoded LOG content into derived `CYCLE`

    This adapter therefore reuses the BIN->LOG workspace first, then invokes the
    later cycle-grouping step on top of those emitted LOG files.
    """

    _validate_inputs(path, config)

    try:
        from tempfile import TemporaryDirectory
        import shutil

        with TemporaryDirectory(prefix="mermaid-bin2cycle-") as tmpdir:
            workdir = Path(tmpdir)
            shutil.copy2(path, workdir / path.name)
            prepare_decode_workspace(workdir, config=config, refresh_database=False)
            decode_workspace_logs(workdir, config=config)
            cycle_paths = derive_workspace_cycles(workdir, config=config)

            for cycle_path in cycle_paths:
                with cycle_path.open("r", encoding="utf-8") as handle:
                    for raw_line in handle:
                        yield raw_line.rstrip("\r\n")
    except Bin2LogError as exc:
        raise Bin2CycleError(str(exc)) from exc


def _run_cycle_grouping(workdir: Path, config: Bin2CycleConfig) -> None:
    """Invoke the external decoder script for the LOG->CYCLE grouping step."""

    harness = """
from pathlib import Path
import os
import runpy
import sys

decoder_script = Path(sys.argv[1]).resolve()
workdir = Path(sys.argv[2]).resolve()

sys.path.insert(0, str(decoder_script.parent))
namespace = runpy.run_path(str(decoder_script))

convert_in_cycle = namespace["convert_in_cycle"]
utc_class = namespace["UTCDateTime"]

workdir_str = str(workdir) + os.sep
convert_in_cycle(workdir_str, utc_class(0), utc_class(32503680000))
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
        raise Bin2CycleError(f"External decoder failed: {detail}")


def derive_workspace_cycles(workdir: Path, *, config: Bin2CycleConfig) -> list[Path]:
    """Derive CYCLE files from decoded LOGs already present in a prepared workspace."""

    if not workdir.exists():
        raise FileNotFoundError(workdir)
    if not workdir.is_dir():
        raise Bin2CycleError(f"Cycle workspace is not a directory: {workdir}")

    _run_cycle_grouping(workdir, config)
    cycle_paths = sorted(workdir.glob("*.CYCLE"))
    if not cycle_paths:
        raise Bin2CycleError(
            f"External decoder did not emit any .CYCLE files for {workdir}."
        )
    return cycle_paths
