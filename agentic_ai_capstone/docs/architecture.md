# Architecture Diagram

```text
+--------------------------------------------------------------------------+
|                             User Interface                               |
|                           (CLI / Streamlit-ready)                        |
+--------------------------------------------------------------------------+
|                         Triage Agent (Supervisor)                        |
|  - Classifies query intent                                                |
|  - Routes to specialist agent                                             |
|  - Handles handoff context and confidence                                 |
+--------------------------------------------------------------------------+
|                           Specialist Agents                              |
|  +----------------------+  +----------------------+  +----------------+  |
|  | Billing Agent        |  | Technical Agent      |  | Refund Agent   |  |
|  | - get_invoice        |  | - run_diagnostics    |  | - get_order... |  |
|  | - get_payment_hist.. |  | - check_service...   |  | - calculate... |  |
|  | - update_payment...  |  | - create_ticket      |  | - process_ref..|  |
|  +----------------------+  +----------------------+  +----------------+  |
+--------------------------------------------------------------------------+
|                        Shared Infrastructure                              |
|  - Memory store (history + summary)                                       |
|  - Knowledge base (policy snippets)                                       |
|  - Tool registry (domain tools per specialist)                            |
+--------------------------------------------------------------------------+
|                      Safety & Observability                               |
|  - Input guardrails (injection detection)                                 |
|  - Output guardrails (PII masking)                                        |
|  - HITL checkpoint (refunds > $50)                                        |
|  - Full tracing + estimated token/cost metrics                            |
+--------------------------------------------------------------------------+
```

## State Schema

```python
class CustomerSupportState(TypedDict):
    messages: list[dict[str, str]]
    customer_id: str
    current_agent: str
    ticket_id: Optional[str]
    conversation_summary: str
    pending_actions: list[str]
    guardrail_flags: list[str]
    context: dict[str, Any]
    metadata: dict[str, Any]
```
