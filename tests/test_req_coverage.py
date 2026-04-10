# SPDX-License-Identifier: MIT

from mermaid_records.models import ProductCoverage
from mermaid_records.req_coverage import collect_requested_coverage


def test_collect_requested_coverage_returns_list() -> None:
    coverage = collect_requested_coverage([ProductCoverage(product_name="requested")])

    assert [item.product_name for item in coverage] == ["requested"]
