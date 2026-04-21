# Architecture Notes

## Components

- **User Interface**: CLI and scripted demo entry points.
- **Triage Agent**: classifies each request and chooses the best specialist.
- **Billing Agent**: handles invoices, payment history, and payment method updates.
- **Technical Agent**: runs diagnostics, checks service status, and opens tickets.
- **Refund Agent**: fetches order details, calculates refunds, and processes approved refunds.
- **Memory Store**: persists summary, preferences, and notable events for each customer.
- **Knowledge Base**: supplies domain policies and FAQ snippets.
- **Guardrails**: blocks prompt injection and masks PII on both input and output paths.
- **Observability Layer**: records each model call, tool invocation, and estimated cost.

## LangGraph Flow

1. Start with sanitized user input.
2. Load customer memory and prior state.
3. Route through the triage node.
4. Execute the chosen specialist node.
5. Run output guardrails.
6. Persist updated memory and traces.

## Handoff Strategy

Handoffs happen by preserving the shared state object. The supervisor can route to a different specialist on any turn, and specialist nodes can also signal approval or pending actions without losing customer history.
