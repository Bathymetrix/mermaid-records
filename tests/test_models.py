from mermaid_timeline.models import (
    AcquisitionWindow,
    LogEvent,
    LogEventType,
    MerRecord,
    ProductCoverage,
    TimelineStatus,
    TimelineStatusKind,
)


def test_dataclasses_can_be_instantiated() -> None:
    record = MerRecord(offset=3, payload=b"abc")
    event = LogEvent(line_number=1, event_type=LogEventType.INFO, message="hello")
    window = AcquisitionWindow(source="log")
    coverage = ProductCoverage(product_name="raw")
    status = TimelineStatus(kind=TimelineStatusKind.OK, detail="ready")

    assert record.offset == 3
    assert event.event_type is LogEventType.INFO
    assert window.source == "log"
    assert coverage.product_name == "raw"
    assert status.kind is TimelineStatusKind.OK
