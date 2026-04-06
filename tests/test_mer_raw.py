from pathlib import Path

from mermaid_timeline.mer_raw import iter_mer_records


def test_iter_mer_records_preserves_payload(tmp_path: Path) -> None:
    path = tmp_path / "sample.MER"
    path.write_bytes(b"first\n\nsecond\n")

    records = list(iter_mer_records(path))

    assert [record.offset for record in records] == [0, 7]
    assert [record.payload for record in records] == [b"first", b"second"]
