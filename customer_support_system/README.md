# Multi-Agent Customer Support System

A production-style, multi-agent customer support assistant built for the
Agentic AI capstone (Phase 2). It demonstrates:

- A **Triage supervisor** that routes inquiries to specialists
- Three **specialist agents** (Billing, Technical, Refund), each with 3 tools
- A **shared tool registry**, **memory store**, and **knowledge base**
- **Input + output guardrails** (prompt-injection block, PII masking, toxicity block)
- **HITL approval** for sensitive actions (refunds > $50)
- End-to-end **tracing + cost tracking** with JSONL export (Langfuse/LangSmith compatible)
- A **25-case automated evaluation suite** with rubric-aligned categories (routing / tools / safety / HITL / memory) — currently **25/25 passing**
- A **CLI** (Gradio/Streamlit pluggable) and an **optional LangGraph adapter**

---

## Quick Start

```bash
cd customer_support_system
pip install -r requirements.txt

# Run automated evaluation (25 test cases, no API keys required)
python -m src.cli eval

# Start interactive chat (mock LLM works offline; set OPENAI_API_KEY for real)
python -m src.cli chat --customer-id cust_001

# Start chat that auto-approves every HITL action (useful for demos)
python -m src.cli chat --customer-id cust_001 --auto-approve

# Run the full unit + integration test suite
pytest
```

### Environment variables

| Variable           | Purpose                                                          |
| ------------------ | ---------------------------------------------------------------- |
| `OPENAI_API_KEY`   | Enables the real OpenAI backend (otherwise a deterministic mock) |
| `CSS_MODEL`        | Model to use, e.g. `gpt-4o-mini`. Default: `mock`                |
| `CSS_TRACE_FILE`   | Append every span as JSONL to this path (trace export)           |

---

## Architecture

```
                        +----------------------------+
                        |  Input Guardrails           |
                        |  (injection, PII mask)      |
                        +-------------+--------------+
                                      |
                                      v
            +-----------------------------------------------+
            |          Triage Agent (Supervisor)            |
            |  - Classifies intent                          |
            |  - Routes to specialist (billing/tech/refund) |
            +------+-----------+-----------+----------------+
                   |           |           |
                   v           v           v
          +-----------+ +-----------+ +-----------+
          |  Billing  | | Technical | |  Refund   |
          | Agent     | | Agent     | | Agent     |
          | - invoice | | - diag    | | - order   |
          | - payment | | - status  | | - calc    |
          | - pay_upd | | - ticket  | | - process |
          +-----+-----+ +-----+-----+ +-----+-----+
                \           |             /
                 v          v            v
            +-------------------------------+
            |  Shared Infrastructure        |
            |  - Tool Registry              |
            |  - Memory Store (per customer)|
            |  - Knowledge Base (FAQs/Docs) |
            +----------------+--------------+
                             |
                             v
            +-------------------------------+
            |  HITL gate (refunds > $50)    |
            |  Output Guardrails            |
            |  (toxicity, PII, secret-leak) |
            +----------------+--------------+
                             |
                             v
            +-------------------------------+
            |  Observability: tracing +     |
            |  cost tracking (JSONL)        |
            +-------------------------------+
```

See [`docs/architecture.md`](docs/architecture.md) for the full spec and
[`docs/state_schema.md`](docs/state_schema.md) for the `CustomerSupportState`
structure.

### Project layout

```
customer_support_system/
├── README.md
├── requirements.txt
├── src/
│   ├── agents/          # TriageAgent, BillingAgent, TechnicalAgent, RefundAgent
│   ├── guardrails/      # Input / output safety filters, PII detection/masking
│   ├── memory/          # JSON-backed customer memory store
│   ├── tools/           # Tool registry + billing/technical/refund mock tools
│   ├── knowledge_base.py
│   ├── llm.py           # OpenAI adapter + deterministic mock fallback
│   ├── observability.py # In-memory tracer, JSONL export, cost tracking
│   ├── orchestrator.py  # Graph-style orchestration of all nodes
│   ├── langgraph_adapter.py # Optional LangGraph StateGraph compile()
│   ├── evaluation.py    # 25-case automated eval suite + scoring
│   ├── cli.py           # CLI: `chat` and `eval` subcommands
│   └── state.py         # CustomerSupportState schema
├── tests/               # 79 pytest unit + integration tests
└── docs/                # Architecture, setup, limitations
```

---

## Framework choice: Why this architecture

The spec listed LangGraph, CrewAI, OpenAI Agents SDK, and AWS Strands as
options. This project implements a **framework-agnostic core** with a
**LangGraph adapter** on top, for two reasons:

1. **Testability.** A pure-Python `Orchestrator` can be unit-tested deterministically without any LLM dependency (`MockLLM` is a keyword-based classifier; OpenAI is plugged in when the key is set). This makes the eval suite runnable in any CI environment.
2. **Portability.** The exact state schema (`CustomerSupportState`) and node
   boundaries (`input_guard → triage → specialist → output_guard`) map 1:1 to a
   LangGraph `StateGraph` (see `src/langgraph_adapter.py`). CrewAI / OpenAI
   Agents SDK can be plugged in by replacing `TriageAgent.classify` and the
   specialists' `handle()` method - everything else (memory, tools, guardrails,
   tracing, HITL) is reused.

**Primary recommendation:** LangGraph. The state-dict + reducer pattern is
exactly the LangGraph mental model, and the adapter in `langgraph_adapter.py`
wires it up when you `pip install langgraph`.

---

## Functional requirements: where they are implemented

| Requirement             | Where                                     | How it is met                                                   |
| ----------------------- | ----------------------------------------- | --------------------------------------------------------------- |
| Multi-Agent Routing (90%+) | `src/agents/triage.py`, `src/llm.py` | 25/25 eval cases pass; routing category is 8/8 (100%)          |
| Tool Integration (≥2/agent) | `src/tools/*`                         | 3 tools per specialist; registry enforces owner + HITL predicate |
| Memory Persistence      | `src/memory/store.py`, `src/orchestrator.py` | JSON-backed; 5+-turn eval case validates context retention |
| Agent Handoffs          | `src/orchestrator.py`                      | Triage classifies every turn; state carries agent + summary     |
| HITL Checkpoints        | `src/tools/registry.py`, `src/tools/refund_tools.py`, `src/orchestrator.py` | Refunds > $50 blocked until approval; AutoApprove/Deny/Queued policies |
| Guardrails              | `src/guardrails/*`                         | Injection block, PII mask, toxicity + secret-leak output filter |
| Observability           | `src/observability.py`                     | Every LLM/tool/guardrail/HITL event traced + priced; JSONL export |
| Evaluation              | `src/evaluation.py`                        | 25 cases across 5 categories, rubric-aligned, JSON report       |

---

## Example: CLI session (HITL refund)

```
$ python -m src.cli chat --customer-id cust_001
You> show my latest invoice
BILLING> Your latest invoice is INV-1003 for $29.00 (status: open, due 2026-03-01).
  [tool] get_invoice ok=True

You> refund order ORD-5002
REFUND> The refund for ORD-5002 is $158.00, which exceeds the $50 approval threshold.
        I've queued it for human review. Once approved I'll process it immediately.
  [tool] get_order_details ok=True
  [tool] calculate_refund ok=True
  [tool] process_refund ok=False (hitl_required=True)
  [HITL] pending: Tool 'process_refund' requires human approval before execution.

=== HUMAN-IN-THE-LOOP APPROVAL REQUIRED ===
{ "tool": "process_refund", "arguments": {"order_id": "ORD-5002", "amount": 158.0, ...} }
Approve? [y/n/q]: y
REFUND> Done - I've processed a $158.00 refund for order ORD-5002.
```

See [`docs/demo.md`](docs/demo.md) for a full scripted demo.

---

## Evaluation: rubric coverage

| Rubric Category    | Weight | Where it is evidenced                                                      |
| ------------------ | ------ | -------------------------------------------------------------------------- |
| Architecture (20%) | ✅     | Clean module boundaries, adapter pattern, framework-agnostic core + LangGraph adapter |
| Functionality (25%)| ✅     | 25/25 eval cases; 3 tools per agent; all FRs implemented                   |
| Safety (20%)       | ✅     | Input injection block, PII mask, output toxicity + secret-leak, HITL gating |
| Observability (15%)| ✅     | Span-based tracing, nested parent/child, per-call cost, JSONL export       |
| Code Quality (10%) | ✅     | Type hints, dataclasses, docstrings, 79 pytest tests                       |
| Evaluation (10%)   | ✅     | 25 cases, automated scoring, JSON report + rubric-aligned categories       |

Run it:

```bash
python -m src.cli eval                      # human-readable report
python -m src.cli eval --json-report e.json # machine-readable report
```

---

## Known limitations

See [`docs/limitations.md`](docs/limitations.md) for the full list. Highlights:

- Mock tools return deterministic canned data. Replace by wiring the
  `src/tools/*_tools.py` functions to real CRM / Billing / Orders APIs.
- The default MockLLM is a keyword-based classifier — set `OPENAI_API_KEY`
  to get true LLM reasoning.
- PII detection is regex-based (emails, phones, SSNs, Luhn-valid cards).
  Swap in Microsoft Presidio / spaCy NER for production coverage.
- Toxicity filter is a small keyword lexicon. Replace with OpenAI moderation
  API or Perspective API for production.
- Memory is JSON on disk. Swap for Redis/Postgres/vector store by
  replacing `MemoryStore`.
- Tracing is in-memory + JSONL. Ship to Langfuse/LangSmith by subscribing to
  `Tracer` span emits (straightforward: replace `_append_jsonl`).

---

## Setup from scratch

```bash
git clone <this-repo>
cd <this-repo>/customer_support_system
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                     # 79 tests
python -m src.cli eval     # 25-case rubric eval
python -m src.cli chat --customer-id cust_001  # interactive demo
```
