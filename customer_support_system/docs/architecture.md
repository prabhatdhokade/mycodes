# Architecture

## System overview

```
  +--------------------------------------------------------+
  |                      User Interface                     |
  |                (CLI, Gradio, Streamlit)                |
  +------------------------+-------------------------------+
                           |
                           v
  +--------------------------------------------------------+
  |                   Input Guardrails                      |
  |  * Prompt-injection detection (regex patterns)          |
  |  * PII detection + masking (email/phone/SSN/credit)     |
  +------------------------+-------------------------------+
                           |
                           v
  +--------------------------------------------------------+
  |                 Triage Agent (Supervisor)               |
  |  * Classify query -> {billing, technical, refund}        |
  |  * Hand off to specialist                                |
  +------------------------+-------------------------------+
                           |
          +----------------+----------------+
          v                v                v
  +--------------+  +---------------+  +--------------+
  | Billing      |  | Technical     |  | Refund       |
  | Agent        |  | Agent         |  | Agent (HITL) |
  +------+-------+  +-------+-------+  +------+-------+
         |                  |                 |
         v                  v                 v
  +--------------------------------------------------------+
  |                   Shared Infrastructure                 |
  |  * Tool Registry (schema + HITL predicates)             |
  |  * Memory Store (customer history, summary, tickets)    |
  |  * Knowledge Base (FAQ / policy / product docs)         |
  +------------------------+-------------------------------+
                           |
                           v
  +--------------------------------------------------------+
  |         HITL gate (refunds > $50 etc.)                 |
  |         Output Guardrails                              |
  |         * Toxicity, PII mask, secret-leak block        |
  +------------------------+-------------------------------+
                           |
                           v
  +--------------------------------------------------------+
  |               Observability (Tracer)                    |
  |  * Per-span trace_id/span_id/parent_id                  |
  |  * Latency, tokens, cost                                |
  |  * JSONL export (Langfuse/LangSmith compatible)         |
  +--------------------------------------------------------+
```

## State schema

Every turn carries a `CustomerSupportState` dict compatible with LangGraph:

```python
class CustomerSupportState(TypedDict):
    messages: Annotated[list, add_messages]
    customer_id: str
    current_agent: str          # billing | technical | refund | triage
    ticket_id: Optional[str]
    conversation_summary: str   # rolling topic summary
    pending_actions: list       # HITL queue
    guardrail_flags: list       # structured safety events
    trace_id: str
    hitl_required: bool
    hitl_decision: Optional[str]  # approve | deny | None
    metadata: dict
```

## Control flow (per turn)

1. **Input guardrails** run on the raw user message.
   - High-severity injection → the turn is blocked and flagged.
   - PII found → the message is redacted before it reaches any agent.
2. **Triage** classifies the sanitized message.
   - Explicit route (billing/technical/refund) always wins over stickiness.
   - Ambiguous (`triage`) keeps the previous specialist (or asks for clarification).
3. **Specialist** handles the message, calling registered tools via the registry.
4. **HITL gate**: if the tool requires human approval and none has been given,
   the action is queued, the turn returns with `hitl_required=True`, and the
   policy (AutoApprove / AutoDeny / Queued / ConsolePrompt) decides next.
5. **Output guardrails** run on the assistant's text.
   - Toxic / PII-bearing / secret-leaking text is replaced with a safe refusal.
6. **Memory** is updated with both messages + a rolling topic summary.
7. **Tracer** emits spans for every LLM call, tool call, router decision,
   guardrail check, and HITL event, each with cost and latency.

## Node mapping to LangGraph

The in-process `Orchestrator` maps cleanly to a LangGraph `StateGraph`. See
`src/langgraph_adapter.py`. Each method becomes a node; edges follow the
control flow above.

## Extension points

| Need                         | Replace                                       |
| ---------------------------- | --------------------------------------------- |
| Real CRM/Billing/Orders API  | `src/tools/*_tools.py` function bodies        |
| Vector retrieval for KB      | `KnowledgeBase.search()`                      |
| Redis/Postgres memory        | `MemoryStore` class                           |
| Langfuse/LangSmith export    | `Tracer._append_jsonl`                        |
| Presidio-based PII           | `src/guardrails/pii.py` + `find_pii()`        |
| OpenAI moderation            | `OutputGuardrails.check`                      |
| Real LLM                     | Set `OPENAI_API_KEY`; `LLMClient` auto-uses   |
