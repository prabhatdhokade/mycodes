"""Evaluation suite entry-point tests."""
from src.evaluation import load_default_suite, run_evaluation


def test_suite_is_20_plus():
    suite = load_default_suite()
    assert len(suite) >= 20


def test_suite_covers_all_categories():
    suite = load_default_suite()
    categories = {c["category"] for c in suite}
    assert {"routing", "tool", "safety", "hitl", "memory"} <= categories


def test_suite_runs_and_meets_rubric():
    suite = load_default_suite()
    report = run_evaluation(suite)
    # We expect at least 90% pass rate (the capstone's stated routing bar).
    assert report.pass_rate >= 0.9, report.format_text()


def test_routing_accuracy_category():
    suite = [c for c in load_default_suite() if c["category"] == "routing"]
    report = run_evaluation(suite)
    assert report.pass_rate >= 0.9, report.format_text()
