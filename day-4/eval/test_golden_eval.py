"""Pytest wrapper around the golden Q&A eval set (Step 19).

Same import/call pattern as the other test_*.py files in this directory
(direct import of the backend module, no HTTP layer needed here since we're
calling retrieval.answer.answer_query directly, matching how test_mcp_server
calls the underlying functions rather than only going through main.py).

Run with: pytest eval/
"""

import pytest

from golden_qa import GOLDEN_QA
from run_golden_eval import run_case


@pytest.mark.parametrize(
    "case", GOLDEN_QA, ids=[c["domain"] for c in GOLDEN_QA]
)
def test_golden_case(case):
    ok, detail = run_case(case)
    assert ok, f"{case['question']!r} failed: {detail}"


def test_golden_set_clears_threshold():
    results = [run_case(case) for case in GOLDEN_QA]
    n_pass = sum(1 for ok, _ in results if ok)
    n_total = len(results)
    pct = 100.0 * n_pass / n_total
    assert pct >= 90.0, f"Golden eval pass rate {pct:.1f}% is below the 90% threshold"
