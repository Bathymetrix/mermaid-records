# SPDX-License-Identifier: MIT

from pathlib import Path

from mermaid_records.discovery import iter_server_mer


def test_iter_server_mer_is_mer_alias(tmp_path: Path) -> None:
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "0001_ABCDEF01.MER").write_bytes(b"")

    paths = list(iter_server_mer(tmp_path))

    assert [path.name for path in paths] == ["0001_ABCDEF01.MER"]
