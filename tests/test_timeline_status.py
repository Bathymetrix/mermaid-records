from mermaid_timeline.models import TimelineStatus, TimelineStatusKind
from mermaid_timeline.timeline_status import collect_timeline_statuses


def test_collect_timeline_statuses_returns_list() -> None:
    statuses = collect_timeline_statuses(
        [TimelineStatus(kind=TimelineStatusKind.PARTIAL, detail="gap")]
    )

    assert statuses[0].detail == "gap"
