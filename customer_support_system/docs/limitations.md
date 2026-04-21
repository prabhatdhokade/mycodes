# Known Limitations

This system is production-structured but intentionally ships with small
footprints so it can run in CI without external services. Below is the
list of known limitations and the recommended fix for each.

## Data sources

- **Tools return mocked data.** `src/tools/billing_tools.py`,
  `src/tools/technical_tools.py`, and `src/tools/refund_tools.py` read from
  in-memory dicts. Replace the function bodies with HTTP calls to your real
  Billing / CRM / Orders APIs. The registry + agent layer do not change.
- **Knowledge base is 8 documents.** Replace `KnowledgeBase` with a vector
  retriever (FAISS / Chroma / pgvector) for production coverage.

## LLM

- **Default LLM is a deterministic mock.** If `OPENAI_API_KEY` is not set,
  `LLMClient` falls back to `mock_generate`, a keyword-based classifier in
  `src/llm.py`. This is fine for tests, demo, and CI. Set the API key to get
  real reasoning; the rest of the system is unchanged.
- **No streaming.** The CLI buffers replies. Add SSE or websocket streaming
  for interactive UX.

## Safety

- **Prompt-injection detector is regex-based.** It covers the common
  jailbreak + override patterns but is not exhaustive. Pair it with an
  LLM-based classifier (OpenAI Moderation or a small fine-tuned classifier)
  for defense-in-depth.
- **PII is regex + Luhn for cards.** Replace with
  [Microsoft Presidio](https://github.com/microsoft/presidio) or spaCy NER
  for multi-language and broader entity coverage.
- **Toxicity filter is a small lexicon.** Replace with OpenAI's moderation
  endpoint or the Perspective API.
- **No explicit refusal policy for out-of-scope questions.** Add a
  "policy" node in the orchestrator after triage.

## Memory

- **JSON file storage, single host.** Replace `MemoryStore` with Redis
  (sessions), Postgres (profiles), and a vector store (semantic recall).
- **Summary is topic-bag, not semantic.** Use an LLM summarization call
  every N turns for richer context.

## HITL

- **The HITL queue is in-process.** In production, push pending actions to a
  durable queue (SQS / Pub-Sub) and surface them in an operator console.
- **Single-reviewer model.** Add RBAC and approval thresholds by role.

## Observability

- **Traces are in-memory + JSONL.** Ship to Langfuse / LangSmith / Honeycomb
  by subscribing to `Tracer`'s span emission (replace `_append_jsonl`).
- **Cost tracking uses hardcoded prices.** Keep `MODEL_PRICING` in sync with
  your LLM provider's billing page, or pull from an SSM parameter.

## Evaluation

- **25 cases.** The rubric asked for 20+. We exercise routing, tools,
  safety, HITL, and memory. Expand per-team by adding to `load_default_suite()`.
- **Assertions are substring + agent checks.** For production, add
  LLM-as-judge checks (GPT-4o grading) and golden-answer diffs.

## UI

- **Only a CLI is implemented.** Gradio/Streamlit scaffolding is listed as
  optional; add `src/ui_gradio.py` that reuses `Orchestrator` directly.

## Tests

- **No concurrency tests.** The `MemoryStore` and `Tracer` use locks but
  concurrent correctness is not explicitly tested. Add stress tests with
  `concurrent.futures` if you plan to serve multi-tenant traffic.
