from mermaid_timeline.acq_windows import collect_acquisition_windows
from mermaid_timeline.models import AcquisitionWindow


def test_collect_acquisition_windows_returns_list() -> None:
    windows = collect_acquisition_windows([AcquisitionWindow(source="test")])

    assert len(windows) == 1
