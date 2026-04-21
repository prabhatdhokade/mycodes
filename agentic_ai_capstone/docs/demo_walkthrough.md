# Demo Walkthrough (5 minutes)

1. Start with a billing query:
   - `python -m agentic_ai_capstone.main --customer-id cust-1001 --message "Need invoice inv-500 and payment history"`
   - Explain triage routing to billing and show tool calls in `pending_actions`.
2. Switch to technical support:
   - `python -m agentic_ai_capstone.main --customer-id cust-1001 --message "Internet outage and error, escalate ticket"`
   - Point out diagnostics + ticket creation and the generated `ticket_id`.
3. Demonstrate memory continuity:
   - Reuse the same customer and ask a follow-up billing question.
   - Show that the response includes prior context from the memory store.
4. Demonstrate HITL checkpoint:
   - `python -m agentic_ai_capstone.main --customer-id cust-1001 --message "Refund order ord-121 for $120"`
   - Show the response indicates human approval is required.
5. Demonstrate approved refund path:
   - `python -m agentic_ai_capstone.main --customer-id cust-1001 --message "Refund order ord-121 for $120" --approve-refund`
   - Highlight successful processing.
6. Close with observability and metrics:
   - Show `tracing` (`llm_calls`, token estimate, cost estimate).
   - Show `metrics` (`iterations`, checkpoints, `time_to_merge_seconds`).
