# SPDX-License-Identifier: MIT

from pathlib import Path
import sys

import pytest

from mermaid_records.bin2log import Bin2LogConfig, Bin2LogError, iter_decoded_log_lines


def test_iter_decoded_log_lines_yields_lines_from_emitted_log(tmp_path: Path) -> None:
    script = tmp_path / "fake_decoder.py"
    script.write_text(
        """
from pathlib import Path

def decrypt_all(path):
    workdir = Path(path)
    log = workdir / "0000_TEST.LOG"
    log.write_text("line one\\nline two\\n", encoding="utf-8")
    return [path]
""",
        encoding="utf-8",
    )
    bin_file = tmp_path / "sample.BIN"
    bin_file.write_bytes(b"raw-bin")

    config = Bin2LogConfig(
        python_executable=Path(sys.executable),
        decoder_script=script,
    )

    lines = list(iter_decoded_log_lines(bin_file, config=config))

    assert lines == ["line one", "line two"]


def test_iter_decoded_log_lines_surfaces_subprocess_failure(tmp_path: Path) -> None:
    script = tmp_path / "fake_decoder_fail.py"
    script.write_text(
        """
raise RuntimeError("decoder boom")
""",
        encoding="utf-8",
    )
    bin_file = tmp_path / "sample.BIN"
    bin_file.write_bytes(b"raw-bin")

    config = Bin2LogConfig(
        python_executable=Path(sys.executable),
        decoder_script=script,
    )

    with pytest.raises(Bin2LogError, match="External decoder failed"):
        list(iter_decoded_log_lines(bin_file, config=config))


def test_iter_decoded_log_lines_requires_emitted_log_file(tmp_path: Path) -> None:
    script = tmp_path / "fake_decoder_no_output.py"
    script.write_text(
        """
def decrypt_all(path):
    return [path]
""",
        encoding="utf-8",
    )
    bin_file = tmp_path / "sample.BIN"
    bin_file.write_bytes(b"raw-bin")

    config = Bin2LogConfig(
        python_executable=Path(sys.executable),
        decoder_script=script,
    )

    with pytest.raises(Bin2LogError, match="did not emit any .LOG files"):
        list(iter_decoded_log_lines(bin_file, config=config))
