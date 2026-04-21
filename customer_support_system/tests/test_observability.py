"""Observability tests."""
import json
import os

from src.observability import Tracer, set_tracer, MODEL_PRICING


def test_span_lifecycle():
    t = Tracer()
    with t.span("llm.test", "llm", trace_id="trace_x", model="gpt-4o-mini") as s:
        s.tokens_in = 1000
        s.tokens_out = 500
    spans = t.spans()
    assert len(spans) == 1
    assert spans[0].name == "llm.test"
    assert spans[0].cost_usd > 0


def test_nested_spans():
    t = Tracer()
    with t.span("outer", "agent", trace_id="tx") as parent:
        with t.span("inner", "tool", trace_id="tx") as child:
            assert child.parent_id == parent.span_id


def test_cost_summary():
    t = Tracer()
    with t.span("a", "llm", trace_id="t", model="gpt-4o-mini") as s:
        s.tokens_in = 1000
        s.tokens_out = 1000
    with t.span("b", "llm", trace_id="t", model="gpt-4o-mini") as s:
        s.tokens_in = 500
        s.tokens_out = 500
    summary = t.summary()
    assert summary["total_spans"] == 2
    assert summary["total_cost_usd"] > 0


def test_jsonl_export(tmp_path):
    path = tmp_path / "trace.jsonl"
    t = Tracer(export_path=str(path))
    with t.span("x", "agent", trace_id="trace_x"):
        pass
    lines = path.read_text().strip().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["name"] == "x"
