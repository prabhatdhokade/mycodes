# Agentic AI Capstone: Customer Support System

Production-ready multi-agent customer support implementation for the shared capstone.

## Highlights

- Real shipped feature: triage-to-specialist multi-agent support workflow
- Framework: LangGraph state graph
- Specialist agents: Billing, Technical, Refund
- Required tools implemented (3 per specialist)
- Shared memory + knowledge base + central tool registry
- Input/output safety guardrails (injection and PII masking)
- HITL checkpoint: refunds above $50 require approval
- Observability: per-step trace events with token/cost estimates
- Metrics: iteration and elapsed merge-time style telemetry
- Evaluation: automated 20+ case scoring suite

## Framework choice and justification

This project uses **LangGraph** as the primary orchestration framework.

Why LangGraph:

1. Explicit graph/state transitions map naturally to triage handoffs.
2. Robust shared state handling simplifies memory persistence across turns.
3. Safety/HITL checks can be inserted at deterministic workflow boundaries.
4. Improves testability by isolating routing and specialist nodes.

## Architecture diagram

- Markdown diagram: `docs/architecture.md`
- SVG diagram: `docs/architecture.svg`

## Setup instructions

```bash
cd agentic_ai_capstone
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
```

## Demo

```bash
python -m agentic_ai_capstone.main \
  --customer-id cust-1001 \
  --message "Please refund order ord-121 for $45"
```

HITL approval path demo:

```bash
python -m agentic_ai_capstone.main \
  --customer-id cust-1001 \
  --message "Please refund order ord-121 for $85" \
  --approve-refund
```

More demo prompts in `docs/demo_walkthrough.md`.

## Repository structure

```text
agentic_ai_capstone/
  src/agentic_ai_capstone/
    agents/
    guardrails/
    memory/
    metrics/
    observability/
    tools/
    app.py
    engine.py
    main.py
    state.py
  tests/
  docs/
```

## Functional requirement mapping

- Multi-agent routing: supervised triage routes to billing/technical/refund.
- Tool integration: each specialist has at least 2 tools (implemented 3 each).
- Memory persistence: memory store retains events and recent messages.
- Agent handoffs: triage writes route metadata, specialist uses same state.
- HITL: refund above $50 blocked unless approval callback returns true.
- Guardrails: injection detection blocks input; output masks PII.
- Observability: all nodes/tools traced with estimated cost.
- Evaluation: >20 automated scoring cases.

## Captured metrics

`IterationTracker` captures:

- `iterations`
- `successful_iterations`
- `failed_iterations`
- `time_to_merge_seconds` (elapsed execution window)
- `checkpoints` timeline

`TraceCollector` captures:

- call count
- estimated tokens
- estimated cost (USD)
- event log

## Known limitations

- Uses deterministic routing and mock tools instead of external production APIs.
- Cost/token estimates are heuristic.
- PII guardrails are regex-based and not exhaustive.
- HITL approval model is synchronous callback; production should use async queue/workflow.

